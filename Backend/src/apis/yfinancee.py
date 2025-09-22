import yfinance as yf
import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.estimator import is_market_open

def get_stock_data(ticker_symbol: str, start_date: str = "2020-01-01", end: str = None, interval: str = "1d") -> pd.DataFrame:
    """
        Fetch historical OHLCV stock data using yfinance.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL", "MSFT").
        start (str): Start date in YYYY-MM-DD format.
        end (str): End date in YYYY-MM-DD format. Defaults to today if None.
        interval (str): Data frequency ("1d", "1h", "15m", etc.).

    Returns:
        pd.DataFrame: Stock data with columns [open, high, low, close, adj close, volume].
    """
    df = yf.download(ticker_symbol, start=start_date, end=end, interval=interval, auto_adjust=True, progress=False)
    df = df.rename(columns=str.lower)
    return df


def fetch_option_data(ticker_symbol: str) -> pd.DataFrame:
    """
    Fetch all available option chain data for a ticker.
    """
    tk = yf.Ticker(ticker_symbol)
    expirations = tk.options
    out = {}

    for exp in expirations:
        chain = tk.option_chain(exp)
        calls = chain.calls.assign(expiration=exp, option_type="call")
        puts = chain.puts.assign(expiration=exp, option_type="put")
        out[exp] = pd.concat([calls, puts], ignore_index=True)

    return out


def get_next_expiry_chain(ticker_symbol: str) -> pd.DataFrame:
    """
    Fetch the nearest-expiry option chain.
    """
    tk = yf.Ticker(ticker_symbol)
    first_exp = tk.options[0]
    chain = tk.option_chain(first_exp)
    calls = chain.calls.assign(expiration=first_exp, option_type="call")
    puts = chain.puts.assign(expiration=first_exp, option_type="put")
    return pd.concat([calls, puts], ignore_index=True)


def get_option_chain_by_expiry(ticker_symbol: str, expiry: str) -> pd.DataFrame:
    """
    Fetch option chain for a given expiry date.
    """
    tk = yf.Ticker(ticker_symbol)

    if expiry not in tk.options:
        raise ValueError(f"Expiry {expiry} not available. Available expiries: {tk.options}")

    chain = tk.option_chain(expiry)
    calls = chain.calls.assign(expiration=expiry, option_type="call")
    puts = chain.puts.assign(expiration=expiry, option_type="put")
    return pd.concat([calls, puts], ignore_index=True)

