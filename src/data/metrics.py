"""
Financial Metrics Calculator
Fetches financial data from yfinance and calculates screening metrics
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import time


def calculate_revenue_cagr(revenues: pd.Series, years: int = 5) -> Optional[float]:
    """
    Calculate Compound Annual Growth Rate for revenue.

    Args:
        revenues: Series of annual revenues (sorted by date)
        years: Number of years to calculate CAGR over

    Returns:
        CAGR as a percentage, or None if insufficient data
    """
    try:
        # Remove NaN values
        revenues = revenues.dropna()

        # Need at least 3 data points for meaningful CAGR (relaxed from years requirement)
        if len(revenues) < 3:
            return None

        # Get oldest and most recent values
        oldest = revenues.iloc[0]
        newest = revenues.iloc[-1]

        if oldest <= 0 or newest <= 0 or pd.isna(oldest) or pd.isna(newest):
            return None

        # Calculate actual time span in years
        date_span = (revenues.index[-1] - revenues.index[0]).days / 365.25
        if date_span < 1:
            return None

        # CAGR = ((Ending Value / Beginning Value) ^ (1 / years)) - 1
        cagr = (pow(newest / oldest, 1 / date_span) - 1) * 100
        return cagr

    except Exception as e:
        return None


def get_stock_metrics(ticker: str, verbose: bool = False) -> Dict:
    """
    Fetch all required financial metrics for a single stock.

    Args:
        ticker: Stock ticker symbol
        verbose: If True, print progress messages

    Returns:
        Dictionary containing all calculated metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Initialize result dictionary
        metrics = {
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
            'sector': info.get('sector', 'Unknown'),
            'market_cap': info.get('marketCap', None),
        }

        # 1. Return on Equity (ROE)
        # ROE = Net Income / Shareholder Equity
        roe = info.get('returnOnEquity', None)
        if roe is not None:
            metrics['roe'] = roe * 100  # Convert to percentage
        else:
            metrics['roe'] = None

        # 2. EBITDA Margin
        # EBITDA Margin = EBITDA / Revenue
        ebitda = info.get('ebitda', None)
        revenue = info.get('totalRevenue', None)
        if ebitda and revenue and revenue > 0:
            metrics['ebitda_margin'] = (ebitda / revenue) * 100
        else:
            # Try alternative calculation using operating margin
            ebitda_margins = info.get('ebitdaMargins', None)
            if ebitda_margins:
                metrics['ebitda_margin'] = ebitda_margins * 100
            else:
                metrics['ebitda_margin'] = None

        # 3. Free Cash Flow Yield
        # FCF Yield = Free Cash Flow / Market Cap
        fcf = info.get('freeCashflow', None)
        market_cap = info.get('marketCap', None)
        if fcf and market_cap and market_cap > 0:
            metrics['fcf_yield'] = (fcf / market_cap) * 100
        else:
            metrics['fcf_yield'] = None

        # 4. Revenue CAGR (5 years)
        # Need historical financials
        try:
            financials = stock.financials
            if not financials.empty and 'Total Revenue' in financials.index:
                revenues = financials.loc['Total Revenue'].sort_index()
                metrics['revenue_cagr_5y'] = calculate_revenue_cagr(revenues, years=5)
            else:
                # Try using quarterly data if annual not available
                quarterly = stock.quarterly_financials
                if not quarterly.empty and 'Total Revenue' in quarterly.index:
                    # Approximate annual from quarterly (use trailing 12 months)
                    metrics['revenue_cagr_5y'] = None  # Skip for now if only quarterly
                else:
                    metrics['revenue_cagr_5y'] = None
        except Exception:
            metrics['revenue_cagr_5y'] = None

        # 5. Debt to Equity Ratio
        # Total Debt / Total Equity
        debt_to_equity = info.get('debtToEquity', None)
        if debt_to_equity is not None:
            metrics['debt_equity'] = debt_to_equity
        else:
            # Try calculating from balance sheet
            total_debt = info.get('totalDebt', None)
            total_equity = info.get('totalStockholderEquity', None)
            if total_debt and total_equity and total_equity > 0:
                metrics['debt_equity'] = (total_debt / total_equity) * 100
            else:
                metrics['debt_equity'] = None

        # 6. Forward P/E Ratio (for Model 3)
        forward_pe = info.get('forwardPE', None)
        metrics['forward_pe'] = forward_pe

        # Additional useful metrics
        metrics['trailing_pe'] = info.get('trailingPE', None)
        metrics['current_price'] = info.get('currentPrice', info.get('regularMarketPrice', None))

        if verbose:
            print(f"  ✓ {ticker}: Successfully fetched metrics")

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


def get_multiple_stocks_metrics(tickers: List[str], delay: float = 0.5, verbose: bool = True) -> pd.DataFrame:
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
        print(f"\nFetching metrics for {len(tickers)} stocks...")

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
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'XOM']
    print("Testing metrics calculator with sample stocks...")

    for ticker in test_tickers:
        print(f"\n{ticker}:")
        metrics = get_stock_metrics(ticker, verbose=True)
        for key, value in metrics.items():
            if key not in ['ticker', 'company_name', 'sector', 'error']:
                print(f"  {key}: {value}")
