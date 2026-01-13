"""
Output Formatter
Handles CSV export and console formatting for results
"""

import pandas as pd
import os
from datetime import datetime
from typing import Optional
import sys
sys.path.append('..')
from src.utils.config import OUTPUT_DIR


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def save_portfolio_to_csv(df: pd.DataFrame, model_name: str, timestamp: Optional[str] = None) -> str:
    """
    Save portfolio to CSV file.

    Args:
        df: Portfolio DataFrame
        model_name: Name of the model
        timestamp: Optional timestamp string, if None uses current time

    Returns:
        Path to saved CSV file
    """
    ensure_output_dir()

    if timestamp is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Clean model name for filename
    clean_name = model_name.replace(' ', '_').replace('(', '').replace(')', '').lower()
    filename = f"{clean_name}_{timestamp}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Select columns to export
    export_cols = [
        'ticker', 'company_name', 'sector', 'allocation_pct',
        'roe', 'ebitda_margin', 'revenue_cagr_5y', 'fcf_yield', 'debt_equity',
        'forward_pe', 'current_price', 'market_cap'
    ]

    # Only include columns that exist in DataFrame
    export_cols = [col for col in export_cols if col in df.columns]

    # Export to CSV
    df[export_cols].to_csv(filepath, index=False, float_format='%.2f')

    return filepath


def print_portfolio_table(df: pd.DataFrame, max_rows: int = 50):
    """
    Print portfolio in a formatted table.

    Args:
        df: Portfolio DataFrame
        max_rows: Maximum number of rows to display
    """
    if df.empty:
        print("  No qualifying stocks")
        return

    # Select key columns for display
    display_cols = [
        'ticker', 'company_name', 'allocation_pct',
        'roe', 'ebitda_margin', 'fcf_yield', 'debt_equity'
    ]

    # Only include columns that exist
    display_cols = [col for col in display_cols if col in df.columns]

    display_df = df[display_cols].head(max_rows).copy()

    # Format numeric columns
    format_dict = {
        'allocation_pct': '{:.2f}%',
        'roe': '{:.1f}%',
        'ebitda_margin': '{:.1f}%',
        'fcf_yield': '{:.1f}%',
        'debt_equity': '{:.1f}%',
    }

    for col, fmt in format_dict.items():
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: fmt.format(x) if pd.notna(x) else 'N/A')

    # Print table
    print("\n" + display_df.to_string(index=False))

    if len(df) > max_rows:
        print(f"\n  ... and {len(df) - max_rows} more stocks")


def save_summary_report(results: dict, timestamp: Optional[str] = None) -> str:
    """
    Save a summary report comparing all models.

    Args:
        results: Dictionary with results from all models
        timestamp: Optional timestamp string

    Returns:
        Path to saved summary file
    """
    ensure_output_dir()

    if timestamp is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    filename = f"summary_report_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w') as f:
        f.write("="*70 + "\n")
        f.write("EEIR SCREENING RESULTS - SUMMARY REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")

        for model_name, (portfolio_df, stats) in results.items():
            f.write(f"\n{model_name}\n")
            f.write("-"*70 + "\n")
            f.write(f"Qualifying stocks: {stats['final_count']}\n")
            f.write(f"Pass rate: {stats['pass_rate']:.1f}%\n")

            if not portfolio_df.empty:
                f.write(f"\nAverage Metrics:\n")
                f.write(f"  ROE: {portfolio_df['roe'].mean():.1f}%\n")
                f.write(f"  EBITDA Margin: {portfolio_df['ebitda_margin'].mean():.1f}%\n")
                f.write(f"  FCF Yield: {portfolio_df['fcf_yield'].mean():.1f}%\n")
                if 'revenue_cagr_5y' in portfolio_df.columns:
                    f.write(f"  Revenue CAGR 5Y: {portfolio_df['revenue_cagr_5y'].mean():.1f}%\n")
                f.write(f"  Debt/Equity: {portfolio_df['debt_equity'].mean():.1f}%\n")

                f.write(f"\nAll Holdings ({len(portfolio_df)} stocks):\n")
                for idx, row in portfolio_df.iterrows():
                    f.write(f"  {row['ticker']:6s} - {row.get('company_name', 'N/A'):30s} "
                           f"({row['allocation_pct']:.2f}%)\n")

            f.write("\n")

    return filepath


def print_comparison_table(results: dict):
    """
    Print a comparison table of all models.

    Args:
        results: Dictionary with results from all models
    """
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)

    comparison_data = []
    for model_name, (portfolio_df, stats) in results.items():
        if not portfolio_df.empty:
            row = {
                'Model': model_name,
                'Stocks': stats['final_count'],
                'Pass Rate': f"{stats['pass_rate']:.1f}%",
                'Avg ROE': f"{portfolio_df['roe'].mean():.1f}%",
                'Avg EBITDA': f"{portfolio_df['ebitda_margin'].mean():.1f}%",
                'Avg FCF Yield': f"{portfolio_df['fcf_yield'].mean():.1f}%",
                'Avg D/E': f"{portfolio_df['debt_equity'].mean():.1f}%",
            }
        else:
            row = {
                'Model': model_name,
                'Stocks': 0,
                'Pass Rate': '0.0%',
                'Avg ROE': 'N/A',
                'Avg EBITDA': 'N/A',
                'Avg FCF Yield': 'N/A',
                'Avg D/E': 'N/A',
            }
        comparison_data.append(row)

    comparison_df = pd.DataFrame(comparison_data)
    print("\n" + comparison_df.to_string(index=False))
    print("\n" + "="*70)


if __name__ == '__main__':
    # Test the formatter
    print("Testing output formatter...")

    # Create sample portfolio
    sample_portfolio = pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'GOOGL'],
        'company_name': ['Apple Inc.', 'Microsoft Corporation', 'Alphabet Inc.'],
        'sector': ['Technology', 'Technology', 'Technology'],
        'allocation_pct': [33.33, 33.33, 33.34],
        'roe': [45.0, 35.0, 18.0],
        'ebitda_margin': [30.0, 40.0, 28.0],
        'fcf_yield': [5.0, 4.5, 3.5],
        'debt_equity': [60.0, 40.0, 10.0],
    })

    # Test table printing
    print("\nTest Portfolio Table:")
    print_portfolio_table(sample_portfolio)

    # Test CSV saving
    ensure_output_dir()
    filepath = save_portfolio_to_csv(sample_portfolio, "Test Model")
    print(f"\nSaved to: {filepath}")
