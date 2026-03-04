"""
Random Forest Classifier that predicts whether a given option contract
will expire In-The-Money (ITM), At-The-Money (ATM), or Out-of-The-Money (OTM).
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score

from ml_engine.data_pipeline import build_moneyness_dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "models")
CLF_MODEL_PATH = os.path.join(MODEL_DIR, "moneyness_rf_model.pkl")
CLF_SCALER_PATH = os.path.join(MODEL_DIR, "moneyness_rf_scaler.pkl")
CLF_ENCODER_PATH = os.path.join(MODEL_DIR, "moneyness_rf_encoder.pkl")
CLF_FEATURES_PATH = os.path.join(MODEL_DIR, "moneyness_rf_features.pkl")

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
    "implied_volatility",
]

TARGET_COL = "moneyness_label"


def train_moneyness_model(
    ticker: str,
    lookback_start: str = "2024-01-01",
    n_estimators: int = 200,
    max_depth: int = 12,
) -> dict:
    """
    Train a Random Forest classifier to predict ITM / ATM / OTM.
    Returns training metrics.
    """
    df = build_moneyness_dataset(ticker, lookback_start)

    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].values
    y_raw = df[TARGET_COL].values

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    clf.fit(X_scaled, y)

    cv_scores = cross_val_score(clf, X_scaled, y, cv=5, scoring="accuracy")

    # Feature importances
    importances = dict(zip(available, clf.feature_importances_.tolist()))
    top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]

    # Save
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(CLF_MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    with open(CLF_SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    with open(CLF_ENCODER_PATH, "wb") as f:
        pickle.dump(le, f)
    with open(CLF_FEATURES_PATH, "wb") as f:
        pickle.dump(available, f)

    # Class distribution
    unique, counts = np.unique(y_raw, return_counts=True)
    dist = dict(zip(unique.tolist(), counts.tolist()))

    return {
        "ticker": ticker,
        "samples": len(df),
        "features_used": len(available),
        "classes": le.classes_.tolist(),
        "class_distribution": dist,
        "cv_accuracy_mean": float(np.mean(cv_scores)),
        "cv_accuracy_std": float(np.std(cv_scores)),
        "train_accuracy": float(clf.score(X_scaled, y)),
        "top_features": top_features,
    }


def _load_moneyness_model():
    """Load persisted classifier artefacts."""
    if not os.path.exists(CLF_MODEL_PATH):
        raise FileNotFoundError(
            "Moneyness RF model not found. Train it first via /ml/train-moneyness."
        )
    with open(CLF_MODEL_PATH, "rb") as f:
        clf = pickle.load(f)
    with open(CLF_SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    with open(CLF_ENCODER_PATH, "rb") as f:
        le = pickle.load(f)
    with open(CLF_FEATURES_PATH, "rb") as f:
        features = pickle.load(f)
    return clf, scaler, le, features


def predict_moneyness(
    ticker: str,
    strike: float,
    expiry: str,
    option_type: str = "call",
    iv_override: float = None,
) -> dict:
    """
    Predict ITM / ATM / OTM for a specific option contract.
    Returns predicted class and class probabilities.
    """
    import yfinance as yf
    from ml_engine.data_pipeline import compute_technical_indicators
    from datetime import datetime

    clf, scaler, le, feature_names = _load_moneyness_model()

    # Build feature vector (same as training)
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

    # If IV not provided, try to fetch from market or use historical vol
    if iv_override is not None:
        iv = iv_override
    else:
        try:
            from apis.yfinancee import get_iv
            iv = get_iv(ticker, expiry, strike, option_type)
        except Exception:
            iv = float(latest.get("hvol_20", 0.3))

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
        "implied_volatility": iv,
    }

    X = np.array([[row.get(f, 0) for f in feature_names]])
    X_scaled = scaler.transform(X)

    pred_idx = clf.predict(X_scaled)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    probas = clf.predict_proba(X_scaled)[0]
    class_probs = {le.inverse_transform([i])[0]: float(p) for i, p in enumerate(probas)}

    return {
        "prediction": pred_label,
        "probabilities": class_probs,
        "spot": spot,
        "strike": strike,
        "moneyness": moneyness,
        "tte": tte,
        "option_type": option_type,
        "iv_used": iv,
    }
