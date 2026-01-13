"""
Backtesting Engine
Simulates portfolio performance with historical price data and rebalancing
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.utils.config import SPX_TICKER
from src.backtesting.performance import calculate_all_metrics


def get_historical_prices(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical adjusted close prices for multiple tickers.

    Args:
        tickers: List of ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with adjusted close prices, tickers as columns, dates as index
    """
    print(f"Fetching historical prices for {len(tickers)} stocks from {start_date} to {end_date}...")

    try:
        # Download data for all tickers
        data = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=False)

        if data.empty:
            print("  No data returned from yfinance")
            return pd.DataFrame()

        # Extract adjusted close prices
        if len(tickers) == 1:
            # Single ticker returns simple DataFrame
            if 'Adj Close' in data.columns:
                prices = data[['Adj Close']].copy()
                prices.columns = tickers
            else:
                print("  No 'Adj Close' column found")
                return pd.DataFrame()
        else:
            # Multiple tickers return MultiIndex DataFrame
            if 'Adj Close' in data.columns.get_level_values(0):
                prices = data['Adj Close'].copy()
            elif 'Close' in data.columns.get_level_values(0):
                # Fallback to Close if Adj Close not available
                prices = data['Close'].copy()
            else:
                print("  No price columns found")
                return pd.DataFrame()

        # Drop columns (tickers) with all NaN values
        prices = prices.dropna(axis=1, how='all')

        if prices.empty:
            print("  All price data is NaN")
            return pd.DataFrame()

        # Forward fill then backward fill missing values
        prices = prices.ffill().bfill()

        print(f"  Successfully fetched data for {len(prices.columns)} stocks")
        if len(prices) > 0:
            print(f"  Date range: {prices.index[0].date()} to {prices.index[-1].date()}")

        return prices

    except Exception as e:
        print(f"Error fetching historical prices: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def get_rebalance_dates(start_date: str, end_date: str, frequency: str = 'annual') -> List[str]:
    """
    Generate rebalancing dates.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        frequency: 'annual' or 'monthly'

    Returns:
        List of rebalancing dates as strings (YYYY-MM-DD)
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    if frequency == 'annual':
        # End of each year
        dates = pd.date_range(start=start, end=end, freq='YE')
    elif frequency == 'monthly':
        # End of each month
        dates = pd.date_range(start=start, end=end, freq='ME')
    else:
        raise ValueError("Frequency must be 'annual' or 'monthly'")

    return [d.strftime('%Y-%m-%d') for d in dates]


def backtest_portfolio(tickers: List[str], start_date: str, end_date: str,
                       rebalance_frequency: str = 'annual', initial_capital: float = 10000) -> Dict:
    """
    Backtest an equal-weighted portfolio with periodic rebalancing.

    Args:
        tickers: List of stock tickers to include in portfolio
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        rebalance_frequency: 'annual' or 'monthly'
        initial_capital: Initial portfolio value

    Returns:
        Dictionary containing portfolio values, benchmark values, and metrics
    """
    if not tickers or len(tickers) == 0:
        print("Error: No tickers provided for backtesting")
        return {}

    # Fetch historical prices
    prices = get_historical_prices(tickers, start_date, end_date)

    if prices.empty:
        print("Error: No price data available")
        return {}

    # Get benchmark (S&P 500) prices
    benchmark_prices = get_historical_prices([SPX_TICKER], start_date, end_date)

    if benchmark_prices.empty:
        print("Warning: Could not fetch benchmark data")
        benchmark_prices = pd.DataFrame(index=prices.index)
        benchmark_prices[SPX_TICKER] = initial_capital

    # Filter tickers to only those with price data
    available_tickers = [t for t in tickers if t in prices.columns]

    if len(available_tickers) == 0:
        print("Error: None of the tickers have price data")
        return {}

    print(f"\nBacktesting {len(available_tickers)} stocks with {rebalance_frequency} rebalancing...")
    print(f"Available tickers: {available_tickers}")

    # Generate rebalancing dates
    rebalance_dates = get_rebalance_dates(start_date, end_date, rebalance_frequency)

    # Initialize portfolio
    portfolio_values = pd.Series(index=prices.index, dtype=float)
    portfolio_values.iloc[0] = initial_capital

    # Equal weight allocation
    weight_per_stock = 1.0 / len(available_tickers)

    # Track holdings (number of shares for each stock)
    holdings = {ticker: 0 for ticker in available_tickers}

    # Initial allocation
    for ticker in available_tickers:
        if pd.notna(prices.loc[prices.index[0], ticker]):
            shares = (initial_capital * weight_per_stock) / prices.loc[prices.index[0], ticker]
            holdings[ticker] = shares

    # Simulate portfolio day by day
    for i, date in enumerate(prices.index):
        # Check if it's a rebalancing date
        if i > 0 and date.strftime('%Y-%m-%d') in rebalance_dates:
            # Rebalance portfolio
            current_value = portfolio_values.iloc[i-1]

            # Sell all holdings
            for ticker in available_tickers:
                holdings[ticker] = 0

            # Buy equal weights
            for ticker in available_tickers:
                if pd.notna(prices.loc[date, ticker]) and prices.loc[date, ticker] > 0:
                    shares = (current_value * weight_per_stock) / prices.loc[date, ticker]
                    holdings[ticker] = shares

        # Calculate portfolio value
        portfolio_value = 0
        for ticker, shares in holdings.items():
            if pd.notna(prices.loc[date, ticker]):
                portfolio_value += shares * prices.loc[date, ticker]

        portfolio_values.iloc[i] = portfolio_value

    # Calculate benchmark returns (buy and hold S&P 500)
    benchmark_values = benchmark_prices[SPX_TICKER] * (initial_capital / benchmark_prices[SPX_TICKER].iloc[0])

    # Calculate performance metrics
    periods_per_year = 252  # Daily data

    metrics = calculate_all_metrics(portfolio_values, benchmark_values, periods_per_year)

    # Add additional info
    metrics['start_date'] = start_date
    metrics['end_date'] = end_date
    metrics['rebalance_frequency'] = rebalance_frequency
    metrics['num_stocks'] = len(available_tickers)
    metrics['tickers'] = available_tickers

    result = {
        'portfolio_values': portfolio_values,
        'benchmark_values': benchmark_values,
        'metrics': metrics,
        'rebalance_dates': rebalance_dates,
    }

    return result


def compare_models(results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compare performance of multiple models.

    Args:
        results: Dictionary mapping model names to backtest results

    Returns:
        DataFrame comparing all models
    """
    comparison_data = []

    for model_name, result in results.items():
        if 'metrics' in result:
            metrics = result['metrics']
            comparison_data.append({
                'Model': model_name,
                'Stocks': metrics.get('num_stocks', 0),
                'Cumulative Return': f"{metrics.get('cumulative_return', 0):.1f}%",
                'Excess Return': f"{metrics.get('excess_return', 0):.1f}%",
                'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.2f}",
                'Sortino Ratio': f"{metrics.get('sortino_ratio', 0):.2f}",
                'Max Drawdown': f"{metrics.get('max_drawdown', 0):.1f}%",
                'Volatility': f"{metrics.get('volatility', 0):.1f}%",
            })

    return pd.DataFrame(comparison_data)


if __name__ == '__main__':
    # Test with sample tickers
    print("Testing backtesting engine...")

    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    start = '2020-01-01'
    end = '2024-12-31'

    result = backtest_portfolio(test_tickers, start, end, rebalance_frequency='annual')

    if result:
        print(f"\nPortfolio Performance:")
        print(f"  Start Value: ${result['portfolio_values'].iloc[0]:,.2f}")
        print(f"  End Value: ${result['portfolio_values'].iloc[-1]:,.2f}")
        print(f"  Return: {result['metrics']['cumulative_return']:.2f}%")
        print(f"  Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
