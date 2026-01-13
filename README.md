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

3. Configure your Financial Modeling Prep API key in `src/utils/config.py`

## Usage

### Current Portfolio Screener

Run the stock screener to get current buy recommendations:

```bash
python scripts/run_screener.py
```

This will:
1. Fetch current S&P 500 constituent list (503 stocks)
2. Download financial metrics for all stocks via FMP API
3. Screen stocks using all three models
4. Generate equal-weighted portfolios
5. Save results to CSV files in the `output/` directory

**Output files:**
- `model_1_YYYYMMDD_HHMMSS.csv` - Model 1 qualifying stocks with metrics
- `model_2_YYYYMMDD_HHMMSS.csv` - Model 2 qualifying stocks with metrics
- `model_3_YYYYMMDD_HHMMSS.csv` - Model 3 qualifying stocks with metrics
- `summary_report_YYYYMMDD_HHMMSS.txt` - Complete holdings list and comparison summary

### Latest Screening Results (January 2026)

**Model 1 (Strict Quality):** 11 stocks (2.2% pass rate)
- ABNB, ACGL, ADBE, COIN, DECK, FDS, LRCX, PHM, PYPL, QCOM, RMD
- Avg ROE: 32.2%, Avg EBITDA Margin: 32.6%, Avg FCF Yield: 7.0%

**Model 2 (Moderate):** 18 stocks (3.6% pass rate)
- All Model 1 stocks plus: ACN, CBOE, REGN, RJF, TRV, ULTA, WRB
- Avg ROE: 28.7%, Avg EBITDA Margin: 29.1%, Avg FCF Yield: 7.5%

**Model 3 (Valuation-Focused):** 16 stocks (3.2% pass rate)
- ACGL, ADBE, APO, COIN, CPAY, DECK, FDS, GOOG, GOOGL, LRCX, META, MRK, PHM, PYPL, RCL, VST
- Avg ROE: 34.3%, Avg EBITDA Margin: 37.2%, Avg FCF Yield: 6.0%

### Backtesting

Run historical performance analysis:

```bash
python scripts/run_backtest.py
```

This will:
1. Fetch historical price data for qualifying stocks
2. Simulate portfolio performance with periodic rebalancing
3. Calculate risk-adjusted metrics (Sharpe, Sortino, Jensen's Alpha, Max Drawdown)
4. Compare against S&P 500 benchmark
5. Generate performance reports and portfolio value time series

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

## Data Sources

**Primary:** Financial Modeling Prep (FMP) API
- Comprehensive fundamental data with 100% data completeness
- Requires API key (sign up at financialmodelingprep.com)
- Used for: ROE, EBITDA Margin, Revenue CAGR, FCF Yield, Debt/Equity, Forward P/E

**Secondary:** Yahoo Finance via `yfinance`
- Historical price data for backtesting
- No API key required

**S&P 500 Constituents:**
- Primary: FMP API endpoint
- Fallback: Hardcoded list of 503 current constituents (updated January 2026)

## Performance (Historical Back-test 2015-2025)

Based on the strategy document:
- **Model 1**: 442% cumulative return (annual rebalancing)
- **Model 2**: 322% cumulative return (annual rebalancing)
- **Model 3**: 459% cumulative return (annual rebalancing)
- **S&P 500 Benchmark**: 189% cumulative return (rebalanced)

All models demonstrated strong risk-adjusted returns with Sharpe ratios > 0.75.

## Limitations

- **Point-in-time data**: Current screening uses latest fundamentals, not historical point-in-time data
- **Survivorship bias**: Backtests use current index constituents, not historical membership
- **Data completeness**: ~1-2% of S&P 500 stocks may have incomplete FMP data
- **Transaction costs**: Not included in backtest simulations
- **Rebalancing timing**: Annual/monthly rebalancing may not match exact historical dates
- **Market impact**: Assumes perfect liquidity with no price impact
- **Past performance**: Does not guarantee future results

## Contributing

This is a personal investment research project. No contributions expected.

## Disclaimer

This software is for educational and research purposes only. It does not constitute investment advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

## License

Proprietary.
