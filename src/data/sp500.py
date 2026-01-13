"""
S&P 500 ticker list fetcher
Fetches current S&P 500 constituents from FMP API or Wikipedia
"""

import pandas as pd
import requests
from typing import List, Optional
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.utils.config import FMP_API_KEY, FMP_BASE_URL


def get_sp500_tickers(use_cache: bool = True) -> List[str]:
    """
    Fetch current S&P 500 ticker list from FMP API or Wikipedia.

    Args:
        use_cache: If True, uses pandas caching mechanism

    Returns:
        List of ticker symbols
    """
    # Try FMP API first
    try:
        url = f"{FMP_BASE_URL}/sp500-constituent?apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                tickers = [item['symbol'] for item in data if 'symbol' in item]
                print(f"Successfully fetched {len(tickers)} S&P 500 tickers from FMP API")
                return tickers
        else:
            print(f"FMP API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching S&P 500 tickers from FMP API: {e}")

    # Try Wikipedia as backup
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]  # First table contains the current constituents

        # Extract ticker symbols
        tickers = df['Symbol'].tolist()

        # Clean tickers (some may have special characters)
        tickers = [ticker.replace('.', '-') for ticker in tickers]

        print(f"Successfully fetched {len(tickers)} S&P 500 tickers from Wikipedia")
        return tickers

    except Exception as e:
        print(f"Error fetching S&P 500 tickers from Wikipedia: {e}")
        print("Falling back to a hardcoded list of major S&P 500 companies")
        return get_fallback_tickers()


def get_fallback_tickers() -> List[str]:
    """
    Returns the complete S&P 500 constituent list (503 tickers as of Jan 2026).
    Source: https://stockanalysis.com/list/sp-500-stocks/
    """
    tickers = [
        'NVDA', 'GOOG', 'GOOGL', 'AAPL', 'MSFT', 'AMZN', 'AVGO', 'META', 'TSLA', 'BRK.B',
        'LLY', 'WMT', 'JPM', 'V', 'ORCL', 'XOM', 'MA', 'JNJ', 'PLTR', 'COST',
        'NFLX', 'BAC', 'MU', 'ABBV', 'HD', 'GE', 'AMD', 'PG', 'CVX', 'UNH',
        'KO', 'WFC', 'GS', 'MS', 'CAT', 'CSCO', 'IBM', 'LRCX', 'MRK', 'RTX',
        'PM', 'AXP', 'AMAT', 'CRM', 'TMO', 'APP', 'TMUS', 'INTC', 'MCD', 'ABT',
        'C', 'LIN', 'ISRG', 'DIS', 'PEP', 'BX', 'KLAC', 'BA', 'SCHW', 'QCOM',
        'BLK', 'APH', 'INTU', 'UBER', 'AMGN', 'TJX', 'BKNG', 'GEV', 'ACN', 'TXN',
        'NEE', 'DHR', 'T', 'VZ', 'SPGI', 'ANET', 'GILD', 'LOW', 'COF', 'NOW',
        'ADI', 'PFE', 'BSX', 'SYK', 'ADBE', 'UNP', 'DE', 'HON', 'PANW', 'WELL',
        'ETN', 'LMT', 'PGR', 'MDT', 'NEM', 'PLD', 'CEG', 'CB', 'KKR', 'COP',
        'CRWD', 'PH', 'VRTX', 'BMY', 'HCA', 'ADP', 'CMCSA', 'HOOD', 'SBUX', 'SNPS',
        'CVS', 'MCK', 'CVNA', 'MO', 'GD', 'NKE', 'CME', 'SO', 'MCO', 'ICE',
        'DASH', 'UPS', 'MMC', 'DUK', 'NOC', 'MMM', 'CDNS', 'HWM', 'SHW', 'CRH',
        'WM', 'MAR', 'TT', 'PNC', 'USB', 'FCX', 'BK', 'ABNB', 'APO', 'ELV',
        'RCL', 'EMR', 'ORLY', 'AMT', 'DELL', 'REGN', 'TDG', 'GM', 'CMI', 'CTAS',
        'EQIX', 'ECL', 'MNST', 'GLW', 'AON', 'ITW', 'CI', 'FDX', 'WMB', 'WDC',
        'MDLZ', 'WBD', 'STX', 'HLT', 'SPG', 'TEL', 'JCI', 'AJG', 'SLB', 'COR',
        'CL', 'CSX', 'COIN', 'RSG', 'NSC', 'PWR', 'MSI', 'TFC', 'LHX', 'TRV',
        'AEP', 'PCAR', 'ROST', 'URI', 'NXPI', 'KMI', 'APD', 'ADSK', 'FTNT', 'VST',
        'AZO', 'SRE', 'IDXX', 'BDX', 'EOG', 'AFL', 'SNDK', 'ARES', 'NDAQ', 'PSX',
        'F', 'ZTS', 'DLR', 'VLO', 'WDAY', 'ALL', 'O', 'PYPL', 'CMG', 'MPC',
        'MET', 'EA', 'AXON', 'D', 'PSA', 'GWW', 'CBRE', 'AME', 'EW', 'CAH',
        'TGT', 'FAST', 'AMP', 'BKR', 'DHI', 'CARR', 'ROK', 'ROP', 'MPWR', 'CTVA',
        'DAL', 'TTWO', 'OKE', 'DDOG', 'MSCI', 'XEL', 'YUM', 'EXC', 'XYZ', 'ETR',
        'FANG', 'EBAY', 'OXY', 'A', 'CCL', 'PRU', 'CTSH', 'IQV', 'VMC', 'EL',
        'GRMN', 'LVS', 'PAYX', 'MLM', 'AIG', 'MCHP', 'GEHC', 'PEG', 'HSY', 'TKO',
        'FICO', 'WAB', 'KR', 'CPRT', 'NUE', 'HIG', 'KDP', 'TRGP', 'RMD', 'UAL',
        'STT', 'CCI', 'FISV', 'FIX', 'ODFL', 'KEYS', 'VTR', 'EXPE', 'ED', 'SYY',
        'TER', 'OTIS', 'LYV', 'PCG', 'FIS', 'WEC', 'IR', 'XYL', 'RJF', 'ACGL',
        'HUM', 'FOXA', 'DG', 'KMB', 'KVUE', 'EQT', 'MTB', 'FITB', 'WTW', 'IBKR',
        'VRSK', 'FOX', 'EXR', 'MTD', 'CHTR', 'ADM', 'LEN', 'VICI', 'EME', 'HPE',
        'ROL', 'ULTA', 'SYF', 'NRG', 'HBAN', 'DOV', 'KHC', 'DXCM', 'NTRS', 'CBOE',
        'TPR', 'DLTR', 'BIIB', 'BRO', 'EFX', 'ATO', 'AEE', 'DTE', 'HAL', 'TSCO',
        'IRM', 'STZ', 'WRB', 'BR', 'PHM', 'CFG', 'FE', 'TDY', 'ES', 'PPL',
        'STE', 'CINF', 'FSLR', 'AWK', 'VLTO', 'AVB', 'CSGP', 'HUBB', 'LDOS', 'RF',
        'STLD', 'CNP', 'WSM', 'OMC', 'LULU', 'EXE', 'JBL', 'PPG', 'DRI', 'ON',
        'EQR', 'WAT', 'TROW', 'GIS', 'CPAY', 'EIX', 'VRSN', 'KEY', 'CNC', 'LUV',
        'DVN', 'IP', 'SW', 'GPN', 'RL', 'L', 'EXPD', 'NVR', 'TPL', 'CMS',
        'NTAP', 'TSN', 'INCY', 'CHD', 'LH', 'PTC', 'CHRW', 'NI', 'ALB', 'AMCR',
        'PFG', 'SBAC', 'JBHT', 'WST', 'PODD', 'DGX', 'BG', 'HPQ', 'PKG', 'TRMB',
        'TYL', 'Q', 'CTRA', 'DOW', 'APTV', 'LII', 'SNA', 'WY', 'DD', 'ZBH',
        'SMCI', 'GPC', 'MKC', 'TTD', 'IFF', 'FTV', 'IT', 'CDW', 'EVRG', 'PNR',
        'LNT', 'HOLX', 'ESS', 'GEN', 'J', 'TXT', 'INVH', 'COO', 'MAA', 'FFIV',
        'HII', 'NWS', 'LYB', 'GDDY', 'BALL', 'SOLV', 'DECK', 'NWSA', 'ERIE', 'NDSN',
        'VTRS', 'AVY', 'MAS', 'BBY', 'DPZ', 'KIM', 'IEX', 'ALLE', 'EG', 'JKHY',
        'BLDR', 'ZBRA', 'BEN', 'PSKY', 'MRNA', 'AKAM', 'UDR', 'REG', 'CLX', 'UHS',
        'IVZ', 'HST', 'SWK', 'CF', 'HRL', 'ALGN', 'BF.B', 'HAS', 'WYNN', 'AIZ',
        'DOC', 'BXP', 'RVTY', 'EPAM', 'CPT', 'GL', 'DAY', 'NCLH', 'FDS', 'CRL',
        'PNW', 'SJM', 'TECH', 'BAX', 'AES', 'AOS', 'TAP', 'POOL', 'MGM', 'ARE',
        'MOH', 'GNRC', 'HSIC', 'APA', 'FRT', 'SWKS', 'PAYC', 'MOS', 'CAG', 'CPB',
        'DVA', 'MTCH', 'LW'
    ]
    # Convert dots to hyphens for yfinance compatibility
    return [ticker.replace('.', '-') for ticker in tickers]


def get_company_info(tickers: List[str]) -> pd.DataFrame:
    """
    Get company name and sector information for given tickers.

    Args:
        tickers: List of ticker symbols

    Returns:
        DataFrame with ticker, name, and sector information
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]

        # Clean ticker symbols
        df['Symbol'] = df['Symbol'].str.replace('.', '-')

        # Filter to requested tickers
        df = df[df['Symbol'].isin(tickers)]

        # Select relevant columns
        info_df = df[['Symbol', 'Security', 'GICS Sector']].copy()
        info_df.columns = ['ticker', 'company_name', 'sector']

        return info_df

    except Exception as e:
        print(f"Warning: Could not fetch company info: {e}")
        # Return minimal dataframe
        return pd.DataFrame({
            'ticker': tickers,
            'company_name': tickers,  # Use ticker as name if info unavailable
            'sector': 'Unknown'
        })


if __name__ == '__main__':
    # Test the module
    tickers = get_sp500_tickers()
    print(f"\nFetched {len(tickers)} tickers")
    print(f"First 10 tickers: {tickers[:10]}")

    # Test company info
    info = get_company_info(tickers[:5])
    print(f"\nCompany info for first 5 tickers:")
    print(info)
