"""
Stock Screening Engine
Applies model criteria to filter qualifying stocks
"""

import pandas as pd
from typing import Dict, List, Tuple
import sys
sys.path.append('..')
from src.utils.config import MODEL_1_CRITERIA, MODEL_2_CRITERIA, MODEL_3_CRITERIA


def screen_stocks(df: pd.DataFrame, criteria: Dict) -> Tuple[pd.DataFrame, Dict]:
    """
    Screen stocks based on given criteria.

    Args:
        df: DataFrame with stock metrics
        criteria: Dictionary with screening criteria

    Returns:
        Tuple of (filtered DataFrame, statistics dictionary)
    """
    initial_count = len(df)
    filtered_df = df.copy()

    stats = {
        'model_name': criteria.get('name', 'Unknown'),
        'initial_count': initial_count,
        'filters_applied': []
    }

    # Apply ROE filter
    if 'roe_min' in criteria:
        roe_threshold = criteria['roe_min']
        before = len(filtered_df)
        filtered_df = filtered_df[filtered_df['roe'] >= roe_threshold]
        after = len(filtered_df)
        stats['filters_applied'].append({
            'filter': f'ROE >= {roe_threshold}%',
            'passed': after,
            'failed': before - after
        })

    # Apply EBITDA Margin filter
    if 'ebitda_margin_min' in criteria:
        ebitda_threshold = criteria['ebitda_margin_min']
        before = len(filtered_df)
        filtered_df = filtered_df[filtered_df['ebitda_margin'] >= ebitda_threshold]
        after = len(filtered_df)
        stats['filters_applied'].append({
            'filter': f'EBITDA Margin >= {ebitda_threshold}%',
            'passed': after,
            'failed': before - after
        })

    # Apply Revenue CAGR filter
    if 'revenue_cagr_5y_min' in criteria:
        cagr_threshold = criteria['revenue_cagr_5y_min']
        before = len(filtered_df)
        filtered_df = filtered_df[filtered_df['revenue_cagr_5y'] >= cagr_threshold]
        after = len(filtered_df)
        stats['filters_applied'].append({
            'filter': f'Revenue CAGR 5Y >= {cagr_threshold}%',
            'passed': after,
            'failed': before - after
        })

    # Apply FCF Yield filter
    if 'fcf_yield_min' in criteria:
        fcf_threshold = criteria['fcf_yield_min']
        before = len(filtered_df)
        filtered_df = filtered_df[filtered_df['fcf_yield'] >= fcf_threshold]
        after = len(filtered_df)
        stats['filters_applied'].append({
            'filter': f'FCF Yield >= {fcf_threshold}%',
            'passed': after,
            'failed': before - after
        })

    # Apply Debt/Equity filter
    if 'debt_equity_max' in criteria:
        debt_threshold = criteria['debt_equity_max']
        before = len(filtered_df)
        filtered_df = filtered_df[filtered_df['debt_equity'] <= debt_threshold]
        after = len(filtered_df)
        stats['filters_applied'].append({
            'filter': f'Debt/Equity <= {debt_threshold}%',
            'passed': after,
            'failed': before - after
        })

    # Apply Forward P/E filter (Model 3)
    if 'forward_pe_max' in criteria:
        pe_threshold = criteria['forward_pe_max']
        before = len(filtered_df)
        # Filter out stocks without forward P/E data
        filtered_df = filtered_df[filtered_df['forward_pe'].notna()]
        filtered_df = filtered_df[filtered_df['forward_pe'] <= pe_threshold]
        after = len(filtered_df)
        stats['filters_applied'].append({
            'filter': f'Forward P/E <= {pe_threshold}',
            'passed': after,
            'failed': before - after
        })

    stats['final_count'] = len(filtered_df)
    stats['pass_rate'] = (len(filtered_df) / initial_count * 100) if initial_count > 0 else 0

    return filtered_df, stats


def screen_model_1(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Screen stocks using Model 1 (Strict Quality) criteria."""
    return screen_stocks(df, MODEL_1_CRITERIA)


def screen_model_2(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Screen stocks using Model 2 (Moderate) criteria."""
    return screen_stocks(df, MODEL_2_CRITERIA)


def screen_model_3(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Screen stocks using Model 3 (Valuation) criteria."""
    return screen_stocks(df, MODEL_3_CRITERIA)


def screen_all_models(df: pd.DataFrame) -> Dict[str, Tuple[pd.DataFrame, Dict]]:
    """
    Screen stocks using all three models.

    Args:
        df: DataFrame with stock metrics

    Returns:
        Dictionary mapping model names to (filtered_df, stats) tuples
    """
    results = {
        'Model 1': screen_model_1(df),
        'Model 2': screen_model_2(df),
        'Model 3': screen_model_3(df),
    }

    return results


def print_screening_stats(stats: Dict):
    """
    Print screening statistics in a readable format.

    Args:
        stats: Statistics dictionary from screen_stocks
    """
    print(f"\n{'='*60}")
    print(f"{stats['model_name']}")
    print(f"{'='*60}")
    print(f"Initial stocks: {stats['initial_count']}")
    print(f"\nFilters applied:")
    for filter_stat in stats['filters_applied']:
        print(f"  {filter_stat['filter']}")
        print(f"    ✓ Passed: {filter_stat['passed']}")
        print(f"    ✗ Failed: {filter_stat['failed']}")
    print(f"\nFinal qualifying stocks: {stats['final_count']}")
    print(f"Pass rate: {stats['pass_rate']:.1f}%")
    print(f"{'='*60}")


if __name__ == '__main__':
    # Test with sample data
    print("Testing screening engine...")

    # Create sample data
    sample_data = pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'TEST1', 'TEST2', 'TEST3'],
        'company_name': ['Apple', 'Microsoft', 'Test 1', 'Test 2', 'Test 3'],
        'roe': [45.0, 35.0, 25.0, 18.0, 10.0],
        'ebitda_margin': [30.0, 40.0, 22.0, 18.0, 12.0],
        'revenue_cagr_5y': [10.0, 12.0, 9.0, 7.0, 5.0],
        'fcf_yield': [5.0, 4.5, 4.2, 3.8, 2.0],
        'debt_equity': [60.0, 40.0, 75.0, 85.0, 120.0],
        'forward_pe': [20.0, 22.0, 24.0, 28.0, 15.0],
    })

    print(f"\nSample data: {len(sample_data)} stocks")

    # Test Model 1
    filtered_1, stats_1 = screen_model_1(sample_data)
    print_screening_stats(stats_1)
    print(f"Qualifying stocks: {filtered_1['ticker'].tolist()}")

    # Test Model 2
    filtered_2, stats_2 = screen_model_2(sample_data)
    print_screening_stats(stats_2)
    print(f"Qualifying stocks: {filtered_2['ticker'].tolist()}")

    # Test Model 3
    filtered_3, stats_3 = screen_model_3(sample_data)
    print_screening_stats(stats_3)
    print(f"Qualifying stocks: {filtered_3['ticker'].tolist()}")
