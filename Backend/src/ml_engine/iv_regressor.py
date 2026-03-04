"""
Ridge Regression model that predicts implied volatility (IV) from
stock indicators and option features, then feeds the predicted IV
into the existing pricing engine to produce an option premium.
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

from ml_engine.data_pipeline import build_iv_dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "models")
IV_MODEL_PATH = os.path.join(MODEL_DIR, "iv_ridge_model.pkl")
IV_SCALER_PATH = os.path.join(MODEL_DIR, "iv_ridge_scaler.pkl")
IV_FEATURES_PATH = os.path.join(MODEL_DIR, "iv_ridge_features.pkl")

# Features used by the model (excluding target)
FEATURE_COLS = [
    "close", "log_close",
    "sma_5", "sma_10", "sma_20", "sma_50",
    "close_over_sma_5", "close_over_sma_10", "close_over_sma_20", "close_over_sma_50",
    "hvol_10", "hvol_20", "hvol_30", "hvol_60",
    "rsi_14", "bb_width", "atr_14",
    "volume", "vol_sma_20", "vol_ratio",
    "spot", "strike", "moneyness", "log_moneyness",
    "tte", "sqrt_tte",
    "option_type_call",
    "open_interest", "bid", "ask", "mid_price",
]

TARGET_COL = "implied_volatility"


def train_iv_model(ticker: str, lookback_start: str = "2024-01-01", alpha: float = 1.0) -> dict:
    """
    Train a Ridge Regression model to predict IV for the given ticker.
    Returns training metrics.
    """
    df = build_iv_dataset(ticker, lookback_start)

    # Keep only columns that exist
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].values
    y = df[TARGET_COL].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = Ridge(alpha=alpha)
    model.fit(X_scaled, y)

    # Cross-validated R² score
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring="r2")

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(IV_MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(IV_SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    with open(IV_FEATURES_PATH, "wb") as f:
        pickle.dump(available, f)

    return {
        "ticker": ticker,
        "samples": len(df),
        "features_used": len(available),
        "cv_r2_mean": float(np.mean(cv_scores)),
        "cv_r2_std": float(np.std(cv_scores)),
        "train_r2": float(model.score(X_scaled, y)),
    }


def _load_iv_model():
    """Load the persisted Ridge model, scaler, and feature list."""
    if not os.path.exists(IV_MODEL_PATH):
        raise FileNotFoundError(
            "IV Ridge model not found. Train it first via /ml/train-iv."
        )
    with open(IV_MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(IV_SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    with open(IV_FEATURES_PATH, "rb") as f:
        features = pickle.load(f)
    return model, scaler, features


def predict_iv(
    ticker: str,
    strike: float,
    expiry: str,
    option_type: str = "call",
) -> dict:
    """
    Predict implied volatility for a specific option contract using the
    trained Ridge Regression model.

    Returns dict with predicted_iv and feature snapshot.
    """
    import yfinance as yf
    from ml_engine.data_pipeline import compute_technical_indicators
    from datetime import datetime

    model, scaler, feature_names = _load_iv_model()

    # Current stock data & indicators
    stock_df = yf.download(ticker, start="2024-01-01", auto_adjust=True, progress=False)
    stock_df = stock_df.rename(columns=str.lower)
    indicators = compute_technical_indicators(stock_df).dropna()
    latest = indicators.iloc[-1]

    tk = yf.Ticker(ticker)
    info = tk.info
    spot = info.get("regularMarketPrice") or info.get("previousClose") or float(stock_df["close"].iloc[-1])

    exp_date = pd.to_datetime(expiry)
    tte = (exp_date - datetime.today()).days / 365.0

    moneyness = spot / strike
    row = {
        **latest.to_dict(),
        "spot": spot,
        "strike": strike,
        "moneyness": moneyness,
        "log_moneyness": np.log(moneyness) if moneyness > 0 else 0,
        "tte": tte,
        "sqrt_tte": np.sqrt(max(tte, 0)),
        "option_type_call": 1 if option_type.lower() == "call" else 0,
        "open_interest": 0,
        "bid": 0,
        "ask": 0,
        "mid_price": 0,
    }

    X = np.array([[row.get(f, 0) for f in feature_names]])
    X_scaled = scaler.transform(X)
    predicted_iv = float(model.predict(X_scaled)[0])

    # Clamp IV to reasonable range
    predicted_iv = max(0.01, min(predicted_iv, 5.0))

    return {
        "predicted_iv": predicted_iv,
        "spot": spot,
        "strike": strike,
        "moneyness": moneyness,
        "tte": tte,
        "option_type": option_type,
    }
