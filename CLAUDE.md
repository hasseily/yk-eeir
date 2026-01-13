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
# Run current portfolio screener (screens all 503 S&P 500 stocks)
python scripts/run_screener.py

# This will:
# 1. Fetch S&P 500 ticker list (503 stocks from hardcoded fallback)
# 2. Download financial metrics using FMP API (takes ~2-3 minutes)
# 3. Apply all three screening models
# 4. Generate equal-weighted portfolios
# 5. Save results to output/ directory (CSV + summary report)
```

### Running Backtests
```bash
# Run historical backtest (5-year default: 2020-2024)
python scripts/run_backtest.py

# This will:
# 1. Screen stocks using current fundamentals
# 2. Fetch historical prices via yfinance
# 3. Simulate annual rebalancing
# 4. Calculate performance metrics vs S&P 500 benchmark
# 5. Export portfolio value time series and comparison report
```

### Testing Individual Modules
```bash
# Test S&P 500 ticker fetcher (returns 503 tickers)
python src/data/sp500.py

# Test FMP API metrics fetcher
python src/data/metrics_fmp.py

# Test legacy yfinance metrics (deprecated)
python src/data/metrics.py

# Test screening engine
python src/models/screener.py

# Test portfolio constructor
python src/models/portfolio.py

# Test backtesting engine
python src/backtesting/engine.py

# Test performance metrics calculator
python src/backtesting/performance.py

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
   - `sp500.py` fetches S&P 500 constituents (503 stocks):
     - Tries FMP API endpoint first
     - Falls back to hardcoded list if API unavailable
   - `metrics_fmp.py` uses Financial Modeling Prep API to fetch:
     - Profile data (company info, sector, market cap, price)
     - Financial ratios (debt/equity, forward P/E)
     - Key metrics (ROE, FCF yield)
     - Income statements and cash flow (for Revenue CAGR, EBITDA margin)
   - `metrics.py` (legacy yfinance implementation, kept for reference)

2. **Screening** (`src/models/`)
   - `screener.py` applies model criteria to filter qualifying stocks
   - Model criteria defined in `src/utils/config.py`
   - Tracks pass/fail stats for each filter

3. **Portfolio Construction** (`src/models/`)
   - `portfolio.py` creates equal-weighted portfolios from screened stocks
   - Calculates allocation percentages (100% / num_stocks)
   - Generates sector distribution and average metrics

4. **Backtesting** (`src/backtesting/`)
   - `engine.py` simulates historical portfolio performance
   - `performance.py` calculates risk-adjusted metrics (Sharpe, Sortino, etc.)
   - Compares against S&P 500 benchmark

5. **Output** (`src/output/`)
   - `formatter.py` exports results to CSV and generates:
     - Individual model CSV files with all holdings
     - Summary report with complete holdings list (not just top 10)

### Key Financial Metrics

All metrics are calculated in `src/data/metrics_fmp.py` using FMP API:

- **ROE (Return on Equity)**: From FMP key-metrics endpoint (returnOnEquity × 100)
- **EBITDA Margin**: EBITDA / Revenue from income statements (calculated over trailing 12 months)
- **Revenue CAGR**: Compound annual growth rate calculated from 5+ years of income statements
- **FCF Yield**: From FMP key-metrics endpoint (freeCashFlowYield × 100)
- **Debt/Equity**: From FMP ratios endpoint (debtToEquityRatio × 100)
- **Forward P/E**: From FMP ratios endpoint (priceEarningsToGrowthRatio)

**Data Quality:**
- FMP API provides ~100% data completeness for S&P 500 stocks
- 4 API calls per stock (profile, ratios, key-metrics, income-statement)
- 0.15s delay between stocks to respect rate limits (~75 seconds for 503 stocks)

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

- **FMP API considerations**:
  - Requires paid subscription for `/stable/` endpoints (higher data quality)
  - Rate limits: 250 requests/minute on paid tier (we use 0.15s delays = ~400/min)
  - Some stocks (~1-2%) may have incomplete historical income statements for Revenue CAGR
  - API key must be configured in `src/utils/config.py`

- **yfinance (for backtesting)**:
  - Historical price data generally reliable
  - Some stocks may have missing adjusted close prices
  - No rate limit guarantees; occasional 403 errors from Yahoo

- **S&P 500 constituents**:
  - Hardcoded list of 503 current constituents (updated January 2026)
  - FMP API endpoint available but may require higher subscription tier
  - Historical backtests use current composition (survivorship bias)
  - Point-in-time index membership not yet implemented

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

- **Screening performance**:
  - Full S&P 500 screen takes ~2-3 minutes (503 stocks × 4 API calls × 0.15s delay)
  - FMP API is significantly faster and more reliable than yfinance
  - Consider implementing persistent caching if running frequently

- **Backtesting performance**:
  - 5-year backtest takes ~1-2 minutes depending on portfolio size
  - Daily price data fetching via yfinance is the bottleneck
  - Performance metrics calculation is fast (vectorized pandas operations)

### Latest Screening Results

**January 2026 Full S&P 500 Screen (503 stocks):**
- Model 1: 11 stocks qualified (2.2% pass rate)
- Model 2: 18 stocks qualified (3.6% pass rate)
- Model 3: 16 stocks qualified (3.2% pass rate)
- Data completeness: 502/503 stocks (99.8%)

### Future Enhancements

1. **Data improvements**:
   - Persistent caching with expiry (reduce API calls for repeated runs)
   - Point-in-time fundamental data (eliminate survivorship bias)
   - Historical S&P 500 constituent data (accurate backtest universe)

2. **Backtesting enhancements**:
   - Point-in-time screening (screen based on historical fundamentals)
   - Transaction cost modeling
   - Tax-aware rebalancing
   - Multiple rebalancing strategies (momentum, value rotation)

3. **Portfolio optimization**:
   - Risk-parity weighting (vs equal-weight)
   - Sector constraints (limit concentration)
   - Position sizing based on conviction scores
   - Factor exposure analysis

## File Reference

### Critical Files

**Configuration & Setup:**
- **`src/utils/config.py`**: All model criteria, FMP API key, configuration constants

**Data Layer:**
- **`src/data/sp500.py`**: S&P 500 ticker list (503 hardcoded + FMP API fallback)
- **`src/data/metrics_fmp.py`**: FMP API integration - core metric calculations (ACTIVE)
- **`src/data/metrics.py`**: Legacy yfinance implementation (DEPRECATED, kept for reference)

**Business Logic:**
- **`src/models/screener.py`**: Filtering logic for all three models
- **`src/models/portfolio.py`**: Equal-weighted portfolio construction

**Backtesting:**
- **`src/backtesting/engine.py`**: Historical simulation with rebalancing
- **`src/backtesting/performance.py`**: Risk-adjusted metrics (Sharpe, Sortino, Jensen's Alpha)

**Entry Points:**
- **`scripts/run_screener.py`**: Current portfolio screener (main user entry point)
- **`scripts/run_backtest.py`**: Historical backtesting runner

**Output:**
- **`src/output/formatter.py`**: CSV export and summary report generation

### Output Files

Generated in `output/` directory:
- `model_1_TIMESTAMP.csv`: Model 1 results with all metrics
- `model_2_TIMESTAMP.csv`: Model 2 results with all metrics
- `model_3_TIMESTAMP.csv`: Model 3 results with all metrics
- `summary_report_TIMESTAMP.txt`: Complete holdings list and comparison across all models
- `backtest_comparison_TIMESTAMP.csv`: Backtest performance comparison
- `backtest_model_X_TIMESTAMP.csv`: Daily portfolio values for backtests

### Asset Files

- **`assets/Enhanced Equity Investment Returns.pdf`**: Original strategy document with backtest results (2015-2025)
- **`assets/historical selections.pdf`**: Point-in-time historical selections (2022-2025) for Model 2 & 3
- **`assets/model metrics.txt`**: Quick reference for model criteria
