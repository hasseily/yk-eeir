# EEIR - Enhanced Equity Investment Returns

A quantitative stock screening system for identifying high-quality S&P 500 stocks based on fundamental financial metrics. Implements three screening models with different risk/return profiles.

## Overview

This project implements the Enhanced Equity Investment Returns (EEIR) strategy, which screens S&P 500 stocks based on:
- **Profitability**: Return on Equity (ROE)
- **Operating Efficiency**: EBITDA Margin
- **Growth**: Revenue CAGR (5 years)
- **Cash Generation**: Free Cash Flow Yield
- **Financial Health**: Debt-to-Equity Ratio
- **Valuation**: Forward P/E Ratio (Model 3 only)

## Three Models

### Model 1 (Strict Quality)
- ROE > 20%
- EBITDA Margin > 20%
- Revenue CAGR 5Y > 8%
- FCF Yield > 4%
- Debt/Equity < 80%

### Model 2 (Moderate)
- ROE > 15% (relaxed)
- EBITDA Margin > 15% (relaxed)
- Revenue CAGR 5Y > 8%
- FCF Yield > 4%
- Debt/Equity < 80%

### Model 3 (Valuation-Focused)
- ROE > 20%
- EBITDA Margin > 20%
- Revenue CAGR 5Y > 8%
- FCF Yield > 3% (relaxed)
- Forward P/E < 25% (added)

## Installation

1. Clone this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Current Portfolio Screener

Run the stock screener to get current buy recommendations:

```bash
python scripts/run_screener.py
```

This will:
1. Fetch current S&P 500 constituent list
2. Download financial metrics for all stocks
3. Screen stocks using all three models
4. Generate equal-weighted portfolios
5. Save results to CSV files in the `output/` directory

**Output files:**
- `model_1_strict_quality_YYYYMMDD_HHMMSS.csv` - Model 1 qualifying stocks
- `model_2_moderate_YYYYMMDD_HHMMSS.csv` - Model 2 qualifying stocks
- `model_3_valuation_YYYYMMDD_HHMMSS.csv` - Model 3 qualifying stocks
- `summary_report_YYYYMMDD_HHMMSS.txt` - Comparison summary

### Backtesting (Coming Soon)

Historical performance analysis:

```bash
python scripts/run_backtest.py
```

## Project Structure

```
yk-eeir/
├── assets/                  # Strategy documentation
├── src/
│   ├── data/               # Data fetching and metrics calculation
│   ├── models/             # Screening and portfolio construction
│   ├── backtesting/        # Backtesting engine
│   ├── output/             # Output formatting
│   └── utils/              # Configuration and utilities
├── scripts/                # Main execution scripts
├── output/                 # Generated CSV files and reports
└── requirements.txt
```

## Data Source

Financial data is sourced from Yahoo Finance via the `yfinance` library. No API key required.

## Performance (Historical Back-test 2015-2025)

Based on the strategy document:
- **Model 1**: 442% cumulative return (annual rebalancing)
- **Model 2**: 322% cumulative return (annual rebalancing)
- **Model 3**: 459% cumulative return (annual rebalancing)
- **S&P 500 Benchmark**: 189% cumulative return (rebalanced)

All models demonstrated strong risk-adjusted returns with Sharpe ratios > 0.75.

## Limitations

- Historical fundamental data availability through yfinance is limited
- Some S&P 500 stocks may have incomplete metrics
- Real-time data may differ from end-of-day data
- Transaction costs not included in backtests
- Past performance does not guarantee future results

## Contributing

This is a personal investment research project. Feel free to fork and adapt for your own use.

## Disclaimer

This software is for educational and research purposes only. It does not constitute investment advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

## License

MIT License - see LICENSE file for details
