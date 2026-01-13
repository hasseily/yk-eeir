"""
Portfolio Constructor
Builds portfolios with equal weighting and allocation calculations
"""

import pandas as pd
from typing import Optional


def create_equal_weight_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create an equal-weighted portfolio from screened stocks.

    Args:
        df: DataFrame with qualifying stocks and their metrics

    Returns:
        DataFrame with allocation percentages added
    """
    if df.empty:
        return df

    portfolio_df = df.copy()

    # Calculate equal weight allocation
    num_stocks = len(portfolio_df)
    allocation_pct = 100.0 / num_stocks

    portfolio_df['allocation_pct'] = allocation_pct

    # Sort by ticker for consistency
    portfolio_df = portfolio_df.sort_values('ticker').reset_index(drop=True)

    return portfolio_df


def get_portfolio_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary statistics for a portfolio.

    Args:
        df: Portfolio DataFrame

    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {
            'num_stocks': 0,
            'total_allocation': 0.0,
        }

    summary = {
        'num_stocks': len(df),
        'total_allocation': df['allocation_pct'].sum(),
        'avg_roe': df['roe'].mean() if 'roe' in df.columns else None,
        'avg_ebitda_margin': df['ebitda_margin'].mean() if 'ebitda_margin' in df.columns else None,
        'avg_fcf_yield': df['fcf_yield'].mean() if 'fcf_yield' in df.columns else None,
        'avg_revenue_cagr_5y': df['revenue_cagr_5y'].mean() if 'revenue_cagr_5y' in df.columns else None,
        'avg_debt_equity': df['debt_equity'].mean() if 'debt_equity' in df.columns else None,
        'avg_forward_pe': df['forward_pe'].mean() if 'forward_pe' in df.columns else None,
    }

    # Sector distribution if available
    if 'sector' in df.columns:
        sector_dist = df.groupby('sector').size()
        summary['sector_distribution'] = sector_dist.to_dict()

    return summary


def print_portfolio_summary(summary: dict, model_name: str = "Portfolio"):
    """
    Print portfolio summary in a readable format.

    Args:
        summary: Summary dictionary from get_portfolio_summary
        model_name: Name of the model
    """
    print(f"\n{'='*60}")
    print(f"{model_name} - Portfolio Summary")
    print(f"{'='*60}")
    print(f"Number of stocks: {summary['num_stocks']}")
    print(f"Total allocation: {summary['total_allocation']:.1f}%")

    if summary['num_stocks'] > 0:
        print(f"\nAverage Metrics:")
        if summary.get('avg_roe'):
            print(f"  ROE: {summary['avg_roe']:.1f}%")
        if summary.get('avg_ebitda_margin'):
            print(f"  EBITDA Margin: {summary['avg_ebitda_margin']:.1f}%")
        if summary.get('avg_fcf_yield'):
            print(f"  FCF Yield: {summary['avg_fcf_yield']:.1f}%")
        if summary.get('avg_revenue_cagr_5y'):
            print(f"  Revenue CAGR 5Y: {summary['avg_revenue_cagr_5y']:.1f}%")
        if summary.get('avg_debt_equity'):
            print(f"  Debt/Equity: {summary['avg_debt_equity']:.1f}%")
        if summary.get('avg_forward_pe'):
            print(f"  Forward P/E: {summary['avg_forward_pe']:.1f}")

        if 'sector_distribution' in summary:
            print(f"\nSector Distribution:")
            for sector, count in sorted(summary['sector_distribution'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / summary['num_stocks']) * 100
                print(f"  {sector}: {count} stocks ({pct:.1f}%)")

    print(f"{'='*60}")


def get_top_stocks(df: pd.DataFrame, n: int = 10, sort_by: str = 'roe') -> pd.DataFrame:
    """
    Get top N stocks from portfolio sorted by a metric.

    Args:
        df: Portfolio DataFrame
        n: Number of top stocks to return
        sort_by: Metric to sort by

    Returns:
        DataFrame with top N stocks
    """
    if df.empty:
        return df

    if sort_by not in df.columns:
        print(f"Warning: {sort_by} not in DataFrame columns. Returning first {n} stocks.")
        return df.head(n)

    return df.nlargest(n, sort_by)


if __name__ == '__main__':
    # Test with sample data
    print("Testing portfolio constructor...")

    sample_data = pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'],
        'company_name': ['Apple', 'Microsoft', 'Alphabet', 'NVIDIA', 'Meta'],
        'sector': ['Technology', 'Technology', 'Technology', 'Technology', 'Technology'],
        'roe': [45.0, 35.0, 18.0, 30.0, 25.0],
        'ebitda_margin': [30.0, 40.0, 28.0, 35.0, 32.0],
        'revenue_cagr_5y': [10.0, 12.0, 15.0, 40.0, 20.0],
        'fcf_yield': [5.0, 4.5, 3.5, 2.8, 4.0],
        'debt_equity': [60.0, 40.0, 10.0, 15.0, 20.0],
        'forward_pe': [20.0, 22.0, 18.0, 35.0, 24.0],
    })

    # Create equal weight portfolio
    portfolio = create_equal_weight_portfolio(sample_data)
    print("\nPortfolio with allocations:")
    print(portfolio[['ticker', 'company_name', 'allocation_pct']])

    # Get summary
    summary = get_portfolio_summary(portfolio)
    print_portfolio_summary(summary, "Test Model")

    # Get top stocks by ROE
    print("\nTop 3 stocks by ROE:")
    top_roe = get_top_stocks(portfolio, n=3, sort_by='roe')
    print(top_roe[['ticker', 'roe', 'allocation_pct']])
