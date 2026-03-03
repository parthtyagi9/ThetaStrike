from fastapi import FastAPI, Query, HTTPException
from src.apis.yfinancee import get_option_chain_by_expiry, get_stock_data, get_iv
from src.pricing_engine.evaluate import EvaluationParams, evaluate_option_price
from src.ml_engine.iv_regressor import train_iv_model, predict_iv
from src.ml_engine.moneyness_classifier import train_moneyness_model, predict_moneyness
from datetime import datetime
import pandas as pd
import yfinance as yf

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React on port 5173) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/option-price")
def option_price(
    model: str = Query("european", enum=["european", "american"]),
    ticker: str = "AAPL",
    expiry: str = "2026-01-16",
    strike: float = 150,
    option_type: str = Query("call", enum=["call", "put"]),
    predict_date: str = None,
    rth: bool = True,
    div_yield: float = 0.0
):
    stock_df = get_stock_data(ticker_symbol=ticker, start_date="2024-01-01")
    tk = yf.Ticker(ticker)
    if div_yield == 0.0:
        info = tk.info
        div_yield = info.get("dividendYield", 0.0) or 0.0
    if rth:
        S_now = stock_df["close"].iloc[-1].item()
    else:
        info = tk.info
        S_now = info.get("preMarketPrice") or info.get("postMarketPrice") or info.get("regularMarketPrice")
    expiry_date = pd.to_datetime(expiry)
    today = datetime.today()
    T_total = (expiry_date - today).days / 365.0

    if predict_date:
        future_date = pd.to_datetime(predict_date)
        t_elapsed = (future_date - today).days / 365.0
    else:
        t_elapsed = 0.0

    r = 0.05
    sigma = get_iv(ticker=ticker, expiry=expiry, strike=strike, option_type=option_type)
    # sigma = 0.2


    params = EvaluationParams(
        model=model,
        option_type=option_type,
        S_future=S_now,
        K=strike,
        T_total=T_total,
        t_elapsed=t_elapsed,
        r=r,
        sigma=sigma,
        steps=500,
        q=div_yield
    )
    price = evaluate_option_price(params)
    return {
        "ticker": ticker,
        "expiry": expiry,
        "strike": strike,
        "option_type": option_type,
        "predict_date": predict_date if predict_date else "today",
        "model": model,
        "rth": rth,
        "spot_price_used": S_now,
        "premium": price
    }

@app.get("/stock/{ticker}/price")
def get_stock_price(ticker: str, period: str = "1d", interval: str = "1m", rth: bool = False):
    tk = yf.Ticker(ticker)
    info = tk.info
    df = tk.history(period=period, interval=interval)

    if df.empty:
        raise HTTPException(status_code=404, detail="No price data found")

    latest = df.iloc[-1]

    outside_rth = info.get("preMarketPrice") or info.get("postMarketPrice") or info.get("regularMarketPrice")

    base = {
        "ticker": ticker.upper(),
        "latest": {
            "datetime": str(latest.name),
            "open": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "close": float(latest["Close"]),
            "volume": int(latest["Volume"]),
        }
    }

    if not rth:
        base["latest"]["outside_rth"] = float(outside_rth) if outside_rth else None

    return base 

@app.get("/stock/{ticker}/history")
def get_stock_history(ticker: str, period: str = "1d", interval: str = "1m"):
    tk = yf.Ticker(ticker)
    # info = tk.info()
    df = tk.history(period=period, interval=interval)
    return{"history": df.tail(5).reset_index().to_dict(orient="records")}


# ──────────────────────────────────────────────────────────────
# ML Endpoints
# ──────────────────────────────────────────────────────────────

@app.get("/ml/train-iv")
def ml_train_iv(ticker: str = "AAPL"):
    """Train the Ridge Regression IV model on live option data for a ticker."""
    try:
        metrics = train_iv_model(ticker)
        return {"status": "ok", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/train-moneyness")
def ml_train_moneyness(ticker: str = "AAPL"):
    """Train the Random Forest moneyness classifier on live option data."""
    try:
        metrics = train_moneyness_model(ticker)
        return {"status": "ok", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/predict-iv")
def ml_predict_iv(
    ticker: str = "AAPL",
    strike: float = 150,
    expiry: str = "2026-01-16",
    option_type: str = Query("call", enum=["call", "put"]),
    model: str = Query("european", enum=["european", "american"]),
    predict_date: str = None,
    div_yield: float = 0.0,
):
    """
    Predict IV using Ridge Regression, then price the option using
    the existing pricing engine with the ML-predicted IV.
    """
    try:
        iv_result = predict_iv(ticker, strike, expiry, option_type)
        predicted_sigma = iv_result["predicted_iv"]

        # Reuse existing pricing engine with ML-predicted IV
        spot = iv_result["spot"]
        expiry_date = pd.to_datetime(expiry)
        today = datetime.today()
        T_total = (expiry_date - today).days / 365.0

        if predict_date:
            future_date = pd.to_datetime(predict_date)
            t_elapsed = (future_date - today).days / 365.0
        else:
            t_elapsed = 0.0

        r = 0.05
        tk = yf.Ticker(ticker)
        if div_yield == 0.0:
            info = tk.info
            div_yield = info.get("dividendYield", 0.0) or 0.0

        params = EvaluationParams(
            model=model,
            option_type=option_type,
            S_future=spot,
            K=strike,
            T_total=T_total,
            t_elapsed=t_elapsed,
            r=r,
            sigma=predicted_sigma,
            steps=500,
            q=div_yield,
        )
        premium = evaluate_option_price(params)

        # Also get market IV for comparison
        try:
            market_iv = get_iv(ticker=ticker, expiry=expiry, strike=strike, option_type=option_type)
        except Exception:
            market_iv = None

        return {
            "ticker": ticker,
            "expiry": expiry,
            "strike": strike,
            "option_type": option_type,
            "model": model,
            "spot_price": spot,
            "ml_predicted_iv": round(predicted_sigma, 4),
            "market_iv": round(market_iv, 4) if market_iv else None,
            "ml_premium": round(premium, 4),
            "moneyness": round(iv_result["moneyness"], 4),
            "tte": round(iv_result["tte"], 4),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/predict-moneyness")
def ml_predict_moneyness(
    ticker: str = "AAPL",
    strike: float = 150,
    expiry: str = "2026-01-16",
    option_type: str = Query("call", enum=["call", "put"]),
):
    """
    Predict whether the option will expire ITM, ATM, or OTM
    using the Random Forest classifier.
    """
    try:
        result = predict_moneyness(ticker, strike, expiry, option_type)
        return {
            "ticker": ticker,
            "expiry": expiry,
            "strike": strike,
            "option_type": option_type,
            "prediction": result["prediction"],
            "probabilities": result["probabilities"],
            "spot_price": result["spot"],
            "moneyness": round(result["moneyness"], 4),
            "tte": round(result["tte"], 4),
            "iv_used": round(result["iv_used"], 4),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api_server:app", host="127.0.0.1", port=8000, reload=True)
