"""
Configuration file for EEIR Financial Models
Defines screening criteria for each model
"""

# Model 1: Strictest quality screening
MODEL_1_CRITERIA = {
    'name': 'Model 1 (Strict Quality)',
    'roe_min': 20.0,                    # ROE > 20%
    'ebitda_margin_min': 20.0,          # EBITDA margin > 20%
    'revenue_cagr_5y_min': 8.0,         # Revenue CAGR 5Y > 8%
    'fcf_yield_min': 4.0,               # Free Cash Flow Yield > 4%
    'debt_equity_max': 80.0,            # Total Debt / Total Equity < 80%
}

# Model 2: Moderate quality screening (relaxed thresholds)
MODEL_2_CRITERIA = {
    'name': 'Model 2 (Moderate)',
    'roe_min': 15.0,                    # ROE > 15%
    'ebitda_margin_min': 15.0,          # EBITDA margin > 15%
    'revenue_cagr_5y_min': 8.0,         # Revenue CAGR 5Y > 8%
    'fcf_yield_min': 4.0,               # Free Cash Flow Yield > 4%
    'debt_equity_max': 80.0,            # Total Debt / Total Equity < 80%
}

# Model 3: Valuation-focused screening (adds P/E filter, relaxes FCF yield)
MODEL_3_CRITERIA = {
    'name': 'Model 3 (Valuation)',
    'roe_min': 20.0,                    # ROE > 20%
    'ebitda_margin_min': 20.0,          # EBITDA margin > 20%
    'revenue_cagr_5y_min': 8.0,         # Revenue CAGR 5Y > 8%
    'fcf_yield_min': 3.0,               # Free Cash Flow Yield > 3% (relaxed)
    'forward_pe_max': 25.0,             # Forward P/E < 25%
}

# All models
ALL_MODELS = [MODEL_1_CRITERIA, MODEL_2_CRITERIA, MODEL_3_CRITERIA]

# Risk-free rate for Sharpe ratio calculations (approximate 10-year average)
RISK_FREE_RATE = 0.02  # 2%

# S&P 500 ticker (for benchmarking)
SPX_TICKER = '^GSPC'

# Output directory
OUTPUT_DIR = 'output'

# Cache settings
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 24

# Financial Modeling Prep API
FMP_API_KEY = 'YyH0BS8b6hVBQ5FTWHv6FWYyznHAUCBN'
FMP_BASE_URL = 'https://financialmodelingprep.com/stable'
