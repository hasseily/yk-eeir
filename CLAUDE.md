# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EEIR (Enhanced Equity Investment Returns)** is a quantitative stock screening system that identifies high-quality S&P 500 stocks based on fundamental financial metrics. The system implements three screening models with different risk/return profiles:

- **Model 1 (Strict Quality)**: Most stringent criteria, targets highest quality stocks
- **Model 2 (Moderate)**: Relaxed ROE and EBITDA thresholds for broader diversification
- **Model 3 (Valuation-Focused)**: Adds forward P/E filter, relaxes FCF yield

The project includes both a current portfolio screener and a backtesting engine for historical performance analysis.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Stock Screener
```bash
# Run current portfolio screener (screens all S&P 500 stocks)
python scripts/run_screener.py

# This will:
# 1. Fetch S&P 500 ticker list from Wikipedia
# 2. Download financial metrics using yfinance
# 3. Apply all three screening models
# 4. Generate equal-weighted portfolios
# 5. Save results to output/ directory
```

### Running Backtests (In Development)
```bash
# Run historical backtest
python scripts/run_backtest.py
```

### Testing Individual Modules
```bash
# Test S&P 500 ticker fetcher
python src/data/sp500.py

# Test financial metrics calculator
python src/data/metrics.py

# Test screening engine
python src/models/screener.py

# Test portfolio constructor
python src/models/portfolio.py

# Test output formatter
python src/output/formatter.py
```

## Architecture

### High-Level Structure

The codebase follows a modular architecture with clear separation of concerns:

```
src/
├── data/           # Data acquisition and metric calculation
├── models/         # Business logic (screening, portfolio construction)
├── backtesting/    # Historical performance analysis
├── output/         # Result formatting and export
└── utils/          # Configuration and utilities
```

### Data Flow

1. **Data Acquisition** (`src/data/`)
   - `sp500.py` fetches current S&P 500 constituents from Wikipedia
   - `metrics.py` uses yfinance to fetch financial data and calculates screening metrics

2. **Screening** (`src/models/`)
   - `screener.py` applies model criteria to filter qualifying stocks
   - Model criteria defined in `src/utils/config.py`

3. **Portfolio Construction** (`src/models/`)
   - `portfolio.py` creates equal-weighted portfolios from screened stocks
   - Calculates allocation percentages (100% / num_stocks)

4. **Output** (`src/output/`)
   - `formatter.py` exports results to CSV and generates console summaries

### Key Financial Metrics

All metrics are calculated in `src/data/metrics.py`:

- **ROE (Return on Equity)**: Net Income / Shareholder Equity
- **EBITDA Margin**: EBITDA / Total Revenue
- **Revenue CAGR**: Compound annual growth rate over 5 years
- **FCF Yield**: Free Cash Flow / Market Cap
- **Debt/Equity**: Total Debt / Total Equity
- **Forward P/E**: Forward 12-month Price-to-Earnings ratio

### Model Criteria

Defined in `src/utils/config.py`:
- Each model is a dictionary with threshold values
- Screening logic in `src/models/screener.py` filters stocks meeting ALL criteria
- Missing data automatically disqualifies a stock

### Portfolio Construction

Equal-weighting approach (from PDF methodology):
- Each qualifying stock receives equal allocation: 100% / N stocks
- No sector balancing or position sizing
- Rebalancing logic (for backtests) will adjust holdings periodically

## Important Notes

### Data Source Limitations

- **yfinance quirks**:
  - Some stocks may have missing fundamental data
  - Historical fundamental data is limited (mainly point-in-time snapshots)
  - Revenue CAGR calculation requires 5+ years of annual financial data
  - API has no rate limit guarantees; we add 0.3s delays between requests

- **S&P 500 constituents**: List is fetched from Wikipedia and represents current composition. Historical backtests should ideally use point-in-time index constituents (not yet implemented).

### Code Conventions

- All financial metrics stored as percentages (e.g., ROE = 25.0 means 25%)
- Except market_cap and current_price which use absolute values
- DataFrames use lowercase column names with underscores (e.g., `debt_equity`)
- File paths use `os.path.join()` for cross-platform compatibility

### Extending the System

**Adding a new screening model:**
1. Define criteria in `src/utils/config.py`
2. Add to `ALL_MODELS` list
3. Create screening function in `src/models/screener.py`
4. Update `screen_all_models()` to include new model

**Adding new metrics:**
1. Add calculation in `src/data/metrics.get_stock_metrics()`
2. Update `filter_valid_metrics()` if metric is required
3. Add to model criteria in config if using for screening
4. Update output columns in `src/output/formatter.py`

### Performance Considerations

- Full S&P 500 screen takes 2-5 minutes (500+ stocks × 0.3s delay)
- Consider implementing persistent caching for metrics (currently in-memory only)
- Backtesting is computationally expensive; optimize by vectorizing calculations

### Future Enhancements

1. **Backtesting engine** (partially implemented):
   - Historical price data fetching
   - Rebalancing logic (monthly/annually)
   - Performance metrics (Sharpe, Sortino, Jensen Alpha)
   - Benchmark comparison

2. **Data improvements**:
   - Persistent caching with expiry
   - Historical S&P 500 constituent data
   - Alternative data sources (Financial Modeling Prep, Alpha Vantage)

3. **Portfolio optimization**:
   - Risk-parity weighting
   - Sector constraints
   - Position sizing based on conviction scores

## File Reference

### Critical Files

- **`src/utils/config.py`**: All model criteria and configuration constants
- **`src/data/metrics.py`**: Core metric calculations (most complex logic)
- **`src/models/screener.py`**: Filtering logic for each model
- **`scripts/run_screener.py`**: Main entry point for users

### Output Files

Generated in `output/` directory:
- `model_1_strict_quality_TIMESTAMP.csv`: Model 1 results
- `model_2_moderate_TIMESTAMP.csv`: Model 2 results
- `model_3_valuation_TIMESTAMP.csv`: Model 3 results
- `summary_report_TIMESTAMP.txt`: Comparison across all models

### Asset Files

- **`assets/Enhanced Equity Investment Returns.pdf`**: Original strategy document with backtest results (2015-2025)
- **`assets/model metrics.txt`**: Quick reference for model criteria
