"""
EEIR Backtesting Runner
Backtests portfolio performance using historical data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
import pandas as pd
from src.data.sp500 import get_sp500_tickers
from src.data.metrics_fmp import get_multiple_stocks_metrics, filter_valid_metrics
from src.models.screener import screen_all_models, print_screening_stats
from src.backtesting.engine import backtest_portfolio, compare_models
from src.backtesting.performance import print_performance_summary
from src.utils.config import OUTPUT_DIR


def main():
    """Main execution function."""
    print("="*70)
    print("EEIR BACKTESTING ENGINE")
    print("Enhanced Equity Investment Returns - Historical Performance Analysis")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Backtest parameters
    start_date = '2020-01-01'  # 5-year backtest
    end_date = '2024-12-31'
    rebalance_frequency = 'annual'  # Can be 'annual' or 'monthly'

    print(f"Backtest Period: {start_date} to {end_date}")
    print(f"Rebalancing: {rebalance_frequency}")
    print()

    # Step 1: Get current screening results
    print("[1/4] Running current stock screening...")
    tickers = get_sp500_tickers()
    print(f"      Fetching metrics for {len(tickers)} stocks...")

    metrics_df = get_multiple_stocks_metrics(tickers, delay=0.15, verbose=False)
    valid_df = filter_valid_metrics(metrics_df)

    print(f"      {len(valid_df)} stocks with complete data")

    if valid_df.empty:
        print("\nError: No stocks with complete data. Exiting.")
        return

    # Screen stocks
    results = screen_all_models(valid_df)

    print(f"\n      Screening Results:")
    for model_name, (filtered_df, stats) in results.items():
        print(f"        {model_name}: {stats['final_count']} stocks")

    # Step 2: Backtest each model
    print(f"\n[2/4] Backtesting portfolios...")
    backtest_results = {}

    for model_name, (filtered_df, stats) in results.items():
        if filtered_df.empty:
            print(f"\n  Skipping {model_name}: No qualifying stocks")
            continue

        print(f"\n  Backtesting {model_name}...")
        tickers_to_test = filtered_df['ticker'].tolist()

        result = backtest_portfolio(
            tickers=tickers_to_test,
            start_date=start_date,
            end_date=end_date,
            rebalance_frequency=rebalance_frequency,
            initial_capital=10000
        )

        if result:
            backtest_results[model_name] = result
            metrics = result['metrics']
            print(f"    Cumulative Return: {metrics['cumulative_return']:.2f}%")
            print(f"    Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"    Max Drawdown: {metrics['max_drawdown']:.2f}%")

    if not backtest_results:
        print("\nNo successful backtests to report.")
        return

    # Step 3: Display detailed results
    print(f"\n[3/4] Detailed Performance Analysis...")

    for model_name, result in backtest_results.items():
        print_performance_summary(result['metrics'], model_name)

    # Step 4: Compare models and save results
    print(f"\n[4/4] Model Comparison and Export...")

    comparison_df = compare_models(backtest_results)
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    print(comparison_df.to_string(index=False))
    print("="*70)

    # Save results to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save comparison table
    comparison_path = os.path.join(OUTPUT_DIR, f'backtest_comparison_{timestamp}.csv')
    comparison_df.to_csv(comparison_path, index=False)
    print(f"\n✓ Saved comparison: {comparison_path}")

    # Save detailed portfolio values for each model
    for model_name, result in backtest_results.items():
        clean_name = model_name.replace(' ', '_').replace('(', '').replace(')', '').lower()

        # Portfolio values over time
        values_df = pd.DataFrame({
            'date': result['portfolio_values'].index,
            'portfolio_value': result['portfolio_values'].values,
            'benchmark_value': result['benchmark_values'].values,
        })

        values_path = os.path.join(OUTPUT_DIR, f'backtest_{clean_name}_{timestamp}.csv')
        values_df.to_csv(values_path, index=False)
        print(f"✓ Saved {model_name} portfolio values: {values_path}")

    # Final summary
    print("\n" + "="*70)
    print("BACKTESTING COMPLETE")
    print("="*70)
    print(f"Backtest Period: {start_date} to {end_date}")
    print(f"Rebalancing: {rebalance_frequency}")
    print()
    print("Models backtested:")
    for model_name in backtest_results.keys():
        print(f"  - {model_name}")
    print()
    print(f"Results saved in: {os.path.abspath(OUTPUT_DIR)}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBacktesting interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during backtesting: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
