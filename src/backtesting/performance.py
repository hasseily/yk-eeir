"""
Performance Calculator
Calculates portfolio performance metrics including Sharpe ratio, returns, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.utils.config import RISK_FREE_RATE


def calculate_returns(portfolio_values: pd.Series) -> pd.Series:
    """
    Calculate periodic returns from portfolio values.

    Args:
        portfolio_values: Series of portfolio values indexed by date

    Returns:
        Series of returns
    """
    return portfolio_values.pct_change().fillna(0)


def calculate_cumulative_returns(portfolio_values: pd.Series) -> pd.Series:
    """
    Calculate cumulative returns from portfolio values.

    Args:
        portfolio_values: Series of portfolio values indexed by date

    Returns:
        Series of cumulative returns
    """
    initial_value = portfolio_values.iloc[0]
    return (portfolio_values / initial_value - 1) * 100


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE,
                           periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe ratio.

    Args:
        returns: Series of periodic returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year (252 for daily, 12 for monthly)

    Returns:
        Sharpe ratio
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    sharpe = np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()
    return sharpe


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE,
                            periods_per_year: int = 252) -> float:
    """
    Calculate Sortino ratio (uses downside deviation instead of total volatility).

    Args:
        returns: Series of periodic returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Sortino ratio
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0

    sortino = np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()
    return sortino


def calculate_max_drawdown(portfolio_values: pd.Series) -> float:
    """
    Calculate maximum drawdown.

    Args:
        portfolio_values: Series of portfolio values

    Returns:
        Maximum drawdown as percentage
    """
    cummax = portfolio_values.cummax()
    drawdown = (portfolio_values - cummax) / cummax
    return drawdown.min() * 100


def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility.

    Args:
        returns: Series of periodic returns
        periods_per_year: Number of periods per year

    Returns:
        Annualized volatility as percentage
    """
    return returns.std() * np.sqrt(periods_per_year) * 100


def calculate_jensens_alpha(portfolio_returns: pd.Series, benchmark_returns: pd.Series,
                            risk_free_rate: float = RISK_FREE_RATE) -> float:
    """
    Calculate Jensen's Alpha.

    Args:
        portfolio_returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Jensen's Alpha
    """
    if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
        return 0.0

    # Align the series
    aligned_returns = pd.DataFrame({
        'portfolio': portfolio_returns,
        'benchmark': benchmark_returns
    }).dropna()

    if len(aligned_returns) == 0:
        return 0.0

    # Calculate beta
    covariance = aligned_returns['portfolio'].cov(aligned_returns['benchmark'])
    benchmark_variance = aligned_returns['benchmark'].var()

    if benchmark_variance == 0:
        return 0.0

    beta = covariance / benchmark_variance

    # Calculate alpha
    portfolio_mean = aligned_returns['portfolio'].mean()
    benchmark_mean = aligned_returns['benchmark'].mean()

    alpha = portfolio_mean - (risk_free_rate + beta * (benchmark_mean - risk_free_rate))

    return alpha * 100  # Return as percentage


def calculate_information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculate Information Ratio.

    Args:
        portfolio_returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns

    Returns:
        Information ratio
    """
    if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
        return 0.0

    # Align the series
    aligned_returns = pd.DataFrame({
        'portfolio': portfolio_returns,
        'benchmark': benchmark_returns
    }).dropna()

    if len(aligned_returns) == 0:
        return 0.0

    active_returns = aligned_returns['portfolio'] - aligned_returns['benchmark']
    tracking_error = active_returns.std()

    if tracking_error == 0:
        return 0.0

    return active_returns.mean() / tracking_error


def calculate_beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculate portfolio beta relative to benchmark.

    Args:
        portfolio_returns: Series of portfolio returns
        benchmark_returns: Series of benchmark returns

    Returns:
        Beta coefficient
    """
    if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
        return 1.0

    # Align the series
    aligned_returns = pd.DataFrame({
        'portfolio': portfolio_returns,
        'benchmark': benchmark_returns
    }).dropna()

    if len(aligned_returns) == 0:
        return 1.0

    covariance = aligned_returns['portfolio'].cov(aligned_returns['benchmark'])
    benchmark_variance = aligned_returns['benchmark'].var()

    if benchmark_variance == 0:
        return 1.0

    return covariance / benchmark_variance


def calculate_all_metrics(portfolio_values: pd.Series, benchmark_values: pd.Series,
                          periods_per_year: int = 252) -> Dict:
    """
    Calculate all performance metrics.

    Args:
        portfolio_values: Series of portfolio values indexed by date
        benchmark_values: Series of benchmark values indexed by date
        periods_per_year: Number of periods per year (252 for daily, 12 for monthly)

    Returns:
        Dictionary with all performance metrics
    """
    # Calculate returns
    portfolio_returns = calculate_returns(portfolio_values)
    benchmark_returns = calculate_returns(benchmark_values)

    # Cumulative returns
    portfolio_cum_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
    benchmark_cum_return = (benchmark_values.iloc[-1] / benchmark_values.iloc[0] - 1) * 100

    # Calculate metrics
    metrics = {
        'cumulative_return': portfolio_cum_return,
        'benchmark_cumulative_return': benchmark_cum_return,
        'excess_return': portfolio_cum_return - benchmark_cum_return,
        'sharpe_ratio': calculate_sharpe_ratio(portfolio_returns, periods_per_year=periods_per_year),
        'sortino_ratio': calculate_sortino_ratio(portfolio_returns, periods_per_year=periods_per_year),
        'max_drawdown': calculate_max_drawdown(portfolio_values),
        'volatility': calculate_volatility(portfolio_returns, periods_per_year=periods_per_year),
        'jensens_alpha': calculate_jensens_alpha(portfolio_returns, benchmark_returns),
        'information_ratio': calculate_information_ratio(portfolio_returns, benchmark_returns),
        'beta': calculate_beta(portfolio_returns, benchmark_returns),
    }

    return metrics


def print_performance_summary(metrics: Dict, model_name: str = "Portfolio"):
    """
    Print performance metrics in a readable format.

    Args:
        metrics: Dictionary of performance metrics
        model_name: Name of the model/portfolio
    """
    print(f"\n{'='*70}")
    print(f"{model_name} - Performance Summary")
    print(f"{'='*70}")
    print(f"Cumulative Return:          {metrics['cumulative_return']:>10.2f}%")
    print(f"Benchmark Return:           {metrics['benchmark_cumulative_return']:>10.2f}%")
    print(f"Excess Return:              {metrics['excess_return']:>10.2f}%")
    print(f"\nRisk-Adjusted Metrics:")
    print(f"Sharpe Ratio:               {metrics['sharpe_ratio']:>10.2f}")
    print(f"Sortino Ratio:              {metrics['sortino_ratio']:>10.2f}")
    print(f"Information Ratio:          {metrics['information_ratio']:>10.2f}")
    print(f"\nRisk Metrics:")
    print(f"Volatility (annualized):    {metrics['volatility']:>10.2f}%")
    print(f"Maximum Drawdown:           {metrics['max_drawdown']:>10.2f}%")
    print(f"Beta:                       {metrics['beta']:>10.2f}")
    print(f"Jensen's Alpha:             {metrics['jensens_alpha']:>10.2f}")
    print(f"{'='*70}")


if __name__ == '__main__':
    # Test with sample data
    print("Testing performance calculator...")

    # Create sample portfolio and benchmark data
    dates = pd.date_range('2020-01-01', '2025-01-01', freq='D')

    # Simulate portfolio with 15% annual return and some volatility
    np.random.seed(42)
    daily_returns = np.random.normal(0.15/252, 0.20/np.sqrt(252), len(dates))
    portfolio_values = pd.Series(10000 * (1 + daily_returns).cumprod(), index=dates)

    # Simulate benchmark with 10% annual return
    daily_benchmark_returns = np.random.normal(0.10/252, 0.15/np.sqrt(252), len(dates))
    benchmark_values = pd.Series(10000 * (1 + daily_benchmark_returns).cumprod(), index=dates)

    # Calculate metrics
    metrics = calculate_all_metrics(portfolio_values, benchmark_values, periods_per_year=252)

    # Print results
    print_performance_summary(metrics, "Test Portfolio")
