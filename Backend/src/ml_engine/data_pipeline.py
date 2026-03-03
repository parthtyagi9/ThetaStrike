"""
Data pipeline for ML models.
Fetches stock + option data from Yahoo Finance,
computes technical indicators as features,
and prepares training datasets for the IV regressor and moneyness classifier.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime


# ---------------------------------------------------------------------------
# Technical indicators
# ---------------------------------------------------------------------------

def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given an OHLCV DataFrame (lowercase columns: open, high, low, close, volume),
    compute common technical indicators used as features.
    """
    out = pd.DataFrame(index=df.index)

    close = df["close"].squeeze()
    high = df["high"].squeeze()
    low = df["low"].squeeze()
    volume = df["volume"].squeeze()

    # Price-based
    out["close"] = close
    out["log_close"] = np.log(close)

    # Moving averages
    for w in [5, 10, 20, 50]:
        out[f"sma_{w}"] = close.rolling(w).mean()
        out[f"close_over_sma_{w}"] = close / out[f"sma_{w}"]

    # Historical (realised) volatility – annualised
    log_ret = np.log(close / close.shift(1))
    for w in [10, 20, 30, 60]:
        out[f"hvol_{w}"] = log_ret.rolling(w).std() * np.sqrt(252)

    # RSI (14-period)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    out["rsi_14"] = 100 - (100 / (1 + rs))

    # Bollinger Band width (20-period)
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    out["bb_width"] = (2 * std20) / sma20

    # Average True Range (14)
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    out["atr_14"] = tr.rolling(14).mean()

    # Volume features
    out["volume"] = volume
    out["vol_sma_20"] = volume.rolling(20).mean()
    out["vol_ratio"] = volume / out["vol_sma_20"]

    return out


# ---------------------------------------------------------------------------
# Build training data for the IV Regressor
# ---------------------------------------------------------------------------

def build_iv_dataset(ticker: str, lookback_start: str = "2024-01-01") -> pd.DataFrame:
    """
    For a given ticker, fetch all available option chains and the underlying
    stock data, then join them to create a flat feature table with target = impliedVolatility.
    """
    tk = yf.Ticker(ticker)

    # Stock history
    stock_df = yf.download(ticker, start=lookback_start, auto_adjust=True, progress=False)
    stock_df = stock_df.rename(columns=str.lower)
    indicators = compute_technical_indicators(stock_df)
    indicators = indicators.dropna()

    if indicators.empty:
        raise ValueError(f"Not enough stock data for {ticker}")

    # Latest indicator row (represents "current" market state for live options)
    latest_indicators = indicators.iloc[-1]

    # Fetch option chains across all available expiries
    rows = []
    info = tk.info
    spot = info.get("regularMarketPrice") or info.get("previousClose") or float(stock_df["close"].iloc[-1])

    for exp in tk.options:
        try:
            chain = tk.option_chain(exp)
        except Exception:
            continue

        exp_date = pd.to_datetime(exp)
        tte = (exp_date - datetime.today()).days / 365.0
        if tte <= 0:
            continue

        for opt_type, opt_df in [("call", chain.calls), ("put", chain.puts)]:
            for _, row in opt_df.iterrows():
                iv = row.get("impliedVolatility", np.nan)
                if pd.isna(iv) or iv <= 0 or iv > 5:
                    continue
                strike = row["strike"]
                moneyness = spot / strike
                rows.append({
                    **latest_indicators.to_dict(),
                    "spot": spot,
                    "strike": strike,
                    "moneyness": moneyness,
                    "log_moneyness": np.log(moneyness),
                    "tte": tte,
                    "sqrt_tte": np.sqrt(tte),
                    "option_type_call": 1 if opt_type == "call" else 0,
                    "open_interest": row.get("openInterest", 0) or 0,
                    "bid": row.get("bid", 0) or 0,
                    "ask": row.get("ask", 0) or 0,
                    "mid_price": ((row.get("bid", 0) or 0) + (row.get("ask", 0) or 0)) / 2,
                    "implied_volatility": iv,
                })

    if not rows:
        raise ValueError(f"No valid option data found for {ticker}")

    df = pd.DataFrame(rows)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    return df


# ---------------------------------------------------------------------------
# Build training data for Moneyness Classifier
# ---------------------------------------------------------------------------

def _label_moneyness(row) -> str:
    """Classify an option as ITM, ATM, or OTM based on moneyness ratio."""
    m = row["moneyness"]  # spot / strike
    is_call = row["option_type_call"] == 1

    if is_call:
        if m > 1.02:
            return "ITM"
        elif m < 0.98:
            return "OTM"
        else:
            return "ATM"
    else:  # put
        if m < 0.98:
            return "ITM"
        elif m > 1.02:
            return "OTM"
        else:
            return "ATM"


def build_moneyness_dataset(ticker: str, lookback_start: str = "2024-01-01") -> pd.DataFrame:
    """
    Build a classification dataset.  Reuses the same fetch as the IV dataset
    but adds a moneyness label column.
    """
    df = build_iv_dataset(ticker, lookback_start)
    df["moneyness_label"] = df.apply(_label_moneyness, axis=1)
    return df
