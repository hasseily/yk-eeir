"""
Financial Metrics Calculator using Financial Modeling Prep API
Fetches financial data from FMP and calculates screening metrics
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.utils.config import FMP_API_KEY, FMP_BASE_URL


def fmp_request(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """
    Make a request to FMP API.

    Args:
        endpoint: API endpoint (e.g., 'ratios')
        params: Additional query parameters

    Returns:
        JSON response as dictionary
    """
    url = f"{FMP_BASE_URL}/{endpoint}"

    # Add API key to params
    if params is None:
        params = {}
    params['apikey'] = FMP_API_KEY

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return {}


def calculate_revenue_cagr(income_statements: List[Dict], years: int = 5) -> Optional[float]:
    """
    Calculate revenue CAGR from income statements.

    Args:
        income_statements: List of income statement dictionaries
        years: Number of years for CAGR calculation

    Returns:
        CAGR as percentage or None
    """
    try:
        if not income_statements or len(income_statements) < 3:
            return None

        # Sort by date (most recent first in FMP)
        statements = sorted(income_statements, key=lambda x: x.get('date', ''), reverse=True)

        # Need at least 3 years of data
        if len(statements) < 3:
            return None

        # Get most recent and oldest revenue
        newest_revenue = statements[0].get('revenue')
        oldest_revenue = statements[min(len(statements)-1, years)].get('revenue')

        if not newest_revenue or not oldest_revenue or oldest_revenue <= 0:
            return None

        # Calculate years between dates
        from datetime import datetime
        newest_date = datetime.strptime(statements[0]['date'], '%Y-%m-%d')
        oldest_date = datetime.strptime(statements[min(len(statements)-1, years)]['date'], '%Y-%m-%d')
        years_diff = (newest_date - oldest_date).days / 365.25

        if years_diff < 1:
            return None

        # CAGR = ((Ending Value / Beginning Value) ^ (1 / years)) - 1
        cagr = (pow(newest_revenue / oldest_revenue, 1 / years_diff) - 1) * 100
        return cagr

    except Exception as e:
        return None


def get_stock_metrics(ticker: str, verbose: bool = False) -> Dict:
    """
    Fetch all required financial metrics for a single stock using FMP API.

    Args:
        ticker: Stock ticker symbol
        verbose: If True, print progress messages

    Returns:
        Dictionary containing all calculated metrics
    """
    try:
        metrics = {
            'ticker': ticker,
            'company_name': ticker,
            'sector': 'Unknown',
            'market_cap': None,
        }

        # 1. Get company profile for basic info
        profile = fmp_request('profile', {'symbol': ticker})
        if profile and isinstance(profile, list) and len(profile) > 0:
            profile_data = profile[0]
            metrics['company_name'] = profile_data.get('companyName', ticker)
            metrics['sector'] = profile_data.get('sector', 'Unknown')
            metrics['market_cap'] = profile_data.get('mktCap')
            metrics['current_price'] = profile_data.get('price')

        # 2. Get financial ratios (Debt/Equity)
        ratios = fmp_request('ratios', {'symbol': ticker, 'period': 'annual', 'limit': 1})
        if ratios and isinstance(ratios, list) and len(ratios) > 0:
            ratio_data = ratios[0]

            # Debt to Equity ratio
            debt_equity = ratio_data.get('debtToEquityRatio')
            metrics['debt_equity'] = debt_equity * 100 if debt_equity is not None else None

            # Forward P/E from ratios
            forward_pe = ratio_data.get('priceToEarningsRatio')
            metrics['forward_pe'] = forward_pe
        else:
            metrics['debt_equity'] = None

        # 3. Get key metrics (ROE, FCF Yield, etc.)
        key_metrics = fmp_request('key-metrics', {'symbol': ticker, 'period': 'annual', 'limit': 1})
        if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
            km_data = key_metrics[0]

            # Return on Equity
            roe = km_data.get('returnOnEquity')
            metrics['roe'] = roe * 100 if roe is not None else None

            # Free Cash Flow Yield
            fcf_yield = km_data.get('freeCashFlowYield')
            metrics['fcf_yield'] = fcf_yield * 100 if fcf_yield is not None else None

            # Use P/E from key metrics if not already set
            if metrics.get('forward_pe') is None:
                forward_pe = km_data.get('peRatio')
                metrics['forward_pe'] = forward_pe

        else:
            if 'roe' not in metrics:
                metrics['roe'] = None
            if 'fcf_yield' not in metrics:
                metrics['fcf_yield'] = None
            if 'forward_pe' not in metrics:
                metrics['forward_pe'] = None

        # 4. Get income statement for EBITDA margin and revenue CAGR
        income = fmp_request('income-statement', {'symbol': ticker, 'period': 'annual', 'limit': 6})
        if income and isinstance(income, list) and len(income) > 0:
            latest = income[0]

            # EBITDA Margin = EBITDA / Revenue
            ebitda = latest.get('ebitda')
            revenue = latest.get('revenue')
            if ebitda and revenue and revenue > 0:
                metrics['ebitda_margin'] = (ebitda / revenue) * 100
            else:
                # Try operating income if EBITDA not available
                operating_income = latest.get('operatingIncome')
                if operating_income and revenue and revenue > 0:
                    metrics['ebitda_margin'] = (operating_income / revenue) * 100
                else:
                    metrics['ebitda_margin'] = None

            # Calculate Revenue CAGR
            metrics['revenue_cagr_5y'] = calculate_revenue_cagr(income, years=5)
        else:
            metrics['ebitda_margin'] = None
            metrics['revenue_cagr_5y'] = None

        # 5. Get better forward P/E from profile if available
        if profile and isinstance(profile, list) and len(profile) > 0:
            profile_data = profile[0]
            # FMP doesn't have forward P/E in profile, use trailing PE as proxy
            trailing_pe = profile_data.get('pe')
            if metrics['forward_pe'] is None and trailing_pe:
                metrics['forward_pe'] = trailing_pe

        # 6. If FCF yield still missing, try to calculate from cash flow statement
        if metrics['fcf_yield'] is None:
            cash_flow = fmp_request('cash-flow-statement', {'symbol': ticker, 'period': 'annual', 'limit': 1})
            if cash_flow and isinstance(cash_flow, list) and len(cash_flow) > 0:
                fcf = cash_flow[0].get('freeCashFlow')
                if fcf and metrics['market_cap'] and metrics['market_cap'] > 0:
                    metrics['fcf_yield'] = (fcf / metrics['market_cap']) * 100

        if verbose:
            print(f"  ✓ {ticker}: Successfully fetched metrics from FMP")

        return metrics

    except Exception as e:
        if verbose:
            print(f"  ✗ {ticker}: Error - {str(e)}")
        return {
            'ticker': ticker,
            'error': str(e),
            'roe': None,
            'ebitda_margin': None,
            'fcf_yield': None,
            'revenue_cagr_5y': None,
            'debt_equity': None,
            'forward_pe': None,
        }


def get_multiple_stocks_metrics(tickers: List[str], delay: float = 0.2, verbose: bool = True) -> pd.DataFrame:
    """
    Fetch metrics for multiple stocks with rate limiting.

    Args:
        tickers: List of ticker symbols
        delay: Delay between API calls in seconds
        verbose: If True, print progress

    Returns:
        DataFrame with all metrics
    """
    all_metrics = []

    if verbose:
        print(f"\nFetching metrics from FMP for {len(tickers)} stocks...")

    for i, ticker in enumerate(tickers):
        if verbose and (i + 1) % 50 == 0:
            print(f"Progress: {i + 1}/{len(tickers)} stocks processed")

        metrics = get_stock_metrics(ticker, verbose=False)
        all_metrics.append(metrics)

        # Rate limiting
        if delay > 0 and i < len(tickers) - 1:
            time.sleep(delay)

    df = pd.DataFrame(all_metrics)

    if verbose:
        print(f"\nCompleted! Fetched data for {len(df)} stocks")
        print(f"Stocks with complete data: {df[df['roe'].notna()].shape[0]}")

    return df


def filter_valid_metrics(df: pd.DataFrame, required_fields: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Filter stocks that have all required metrics.

    Args:
        df: DataFrame with stock metrics
        required_fields: List of required field names, if None uses default set

    Returns:
        Filtered DataFrame with only stocks having all required metrics
    """
    if required_fields is None:
        required_fields = ['roe', 'ebitda_margin', 'fcf_yield', 'revenue_cagr_5y', 'debt_equity']

    # Filter rows where all required fields are not null
    mask = df[required_fields].notna().all(axis=1)
    filtered_df = df[mask].copy()

    return filtered_df


if __name__ == '__main__':
    # Test the module with a few stocks
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'MRK', 'V']
    print("Testing FMP metrics calculator with sample stocks...")

    for ticker in test_tickers:
        print(f"\n{ticker}:")
        metrics = get_stock_metrics(ticker, verbose=True)
        for key, value in metrics.items():
            if key not in ['ticker', 'company_name', 'sector', 'error', 'market_cap', 'current_price']:
                if value is not None:
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: None")
