"""
EEIR Stock Screener
Main script to screen S&P 500 stocks using all three models
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.data.sp500 import get_sp500_tickers, get_company_info
from src.data.metrics_fmp import get_multiple_stocks_metrics, filter_valid_metrics
from src.models.screener import screen_all_models, print_screening_stats
from src.models.portfolio import create_equal_weight_portfolio, get_portfolio_summary, print_portfolio_summary
from src.output.formatter import (
    save_portfolio_to_csv, print_portfolio_table,
    save_summary_report, print_comparison_table
)


def main():
    """Main execution function."""
    print("="*70)
    print("EEIR STOCK SCREENER")
    print("Enhanced Equity Investment Returns - Three Model Analysis")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Fetch S&P 500 tickers
    print("\n[1/5] Fetching S&P 500 ticker list...")
    tickers = get_sp500_tickers()
    print(f"      Found {len(tickers)} tickers")

    # Step 2: Fetch financial metrics for all stocks
    print("\n[2/5] Fetching financial metrics from Financial Modeling Prep API...")
    print("      This may take several minutes...")
    metrics_df = get_multiple_stocks_metrics(tickers, delay=0.15, verbose=True)

    # Filter stocks with complete data
    print("\n[3/5] Filtering stocks with complete data...")
    valid_df = filter_valid_metrics(metrics_df)
    print(f"      {len(valid_df)} stocks have all required metrics")
    print(f"      {len(metrics_df) - len(valid_df)} stocks excluded due to missing data")

    if valid_df.empty:
        print("\nError: No stocks with complete data found. Exiting.")
        return

    # Step 3: Screen stocks using all three models
    print("\n[4/5] Screening stocks using all three models...")
    results = screen_all_models(valid_df)

    # Create portfolios
    portfolios = {}
    for model_name, (filtered_df, stats) in results.items():
        print_screening_stats(stats)

        # Create equal-weight portfolio
        portfolio_df = create_equal_weight_portfolio(filtered_df)
        portfolios[model_name] = portfolio_df

        # Print portfolio summary
        summary = get_portfolio_summary(portfolio_df)
        print_portfolio_summary(summary, model_name)

        # Print top holdings
        if not portfolio_df.empty:
            print(f"\nTop 20 Holdings - {model_name}:")
            print_portfolio_table(portfolio_df, max_rows=20)

    # Step 4: Save results
    print("\n[5/5] Saving results to CSV files...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    saved_files = []
    for model_name, (filtered_df, stats) in results.items():
        portfolio_df = portfolios[model_name]
        if not portfolio_df.empty:
            filepath = save_portfolio_to_csv(portfolio_df, model_name, timestamp)
            saved_files.append(filepath)
            print(f"      ✓ Saved {model_name}: {filepath}")
        else:
            print(f"      ✗ Skipped {model_name}: No qualifying stocks")

    # Save summary report - need to pass portfolios instead of filtered results
    portfolio_results = {model_name: (portfolios[model_name], stats)
                        for model_name, (filtered_df, stats) in results.items()}
    summary_path = save_summary_report(portfolio_results, timestamp)
    print(f"      ✓ Saved summary report: {summary_path}")

    # Print comparison table
    print_comparison_table(portfolio_results)

    # Final summary
    print("\n" + "="*70)
    print("SCREENING COMPLETE")
    print("="*70)
    print(f"Total S&P 500 stocks analyzed: {len(tickers)}")
    print(f"Stocks with complete data: {len(valid_df)}")
    print()
    print("Results:")
    for model_name, (filtered_df, stats) in results.items():
        print(f"  {model_name}: {stats['final_count']} qualifying stocks")
    print()
    print(f"Output files saved in: {os.path.abspath('output')}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScreening interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during screening: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
