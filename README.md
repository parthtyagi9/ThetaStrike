# ThetaStrike

Options pricing and analytics platform. FastAPI backend, React frontend.

Prices European options (Black-Scholes) and American options (Binomial Tree), with two ML models layered on top:
- **Ridge Regression** — predicts implied volatility from stock indicators, then feeds it into the pricing engine to produce an ML-driven premium
- **Random Forest Classifier** — predicts whether an option will expire ITM, ATM, or OTM

Market data pulled live from Yahoo Finance via yfinance.

---

## Project Structure
 
```
Backend/
  src/
    api_server.py            # FastAPI app — all endpoints
    core/
      black_scholes.py       # European option pricing
      binomial.py            # American option pricing (CRR tree)
      estimator.py           # Market hours helper
    apis/
      yfinancee.py           # Stock data, option chains, IV fetcher
    pricing_engine/
      evaluate.py            # Unified pricing wrapper
    ml_engine/
      data_pipeline.py       # Feature engineering (technicals + option features)
      iv_regressor.py        # Ridge Regression for IV prediction
      moneyness_classifier.py # Random Forest for ITM/ATM/OTM
  data/
    models/                  # Persisted .pkl model files (gitignored)
  test/
    test_backend.py
    test_pricing.py

Frontend/
  src/
    App.js                   # Root component with tab navigation
    App.css                  # All styles
    components/
      OptionForm.js          # Black-Scholes / Binomial pricing form
      MLPredictions.js       # ML training + prediction interface
```

## Setup

### Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn src.api_server:app --reload
```

Runs on `http://127.0.0.1:8000`. Swagger docs at `/docs`.

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`.

## API Endpoints

### Pricing

```
GET /option-price?model=american&ticker=NVDA&expiry=2026-01-30&strike=200&option_type=call
```

Returns `{ ticker, expiry, strike, option_type, model, spot_price_used, premium }`.

### Stock Data

```
GET /stock/{ticker}/price?period=1d&interval=1m
GET /stock/{ticker}/history?period=5d&interval=1d
```

### ML

```
GET /ml/train-iv?ticker=NVDA              # train Ridge Regression on live option chains
GET /ml/train-moneyness?ticker=NVDA       # train Random Forest classifier

GET /ml/predict-iv?ticker=NVDA&strike=200&expiry=2026-01-30&option_type=call&model=european
GET /ml/predict-moneyness?ticker=NVDA&strike=200&expiry=2026-01-30&option_type=call
```

`predict-iv` returns the ML-predicted IV, market IV for comparison, and the resulting premium.
`predict-moneyness` returns the predicted class (ITM/ATM/OTM) with probability scores.

## ML Details

### IV Regressor (Ridge Regression)

Features: ~30 inputs including SMA ratios, historical volatility (10/20/30/60d), RSI, Bollinger Band width, ATR, volume ratios, moneyness, log-moneyness, time to expiry, and option type. Target is the market-quoted implied volatility. The predicted IV is plugged into the same Black-Scholes or Binomial engine used by the standard pricing endpoint.

### Moneyness Classifier (Random Forest)

Same feature set plus the IV itself. Labels are derived from current moneyness ratio: ITM if S/K > 1.02 for calls (< 0.98 for puts), OTM if opposite, ATM if within 2%. Uses balanced class weights and 200 estimators.

Both models are trained on-demand per ticker against all available option chains and persisted to `data/models/`.

## Tech Stack

| | |
|---|---|
| Frontend | React, Vite |
| Backend | FastAPI, Python 3.10+ |
| Pricing | Black-Scholes, CRR Binomial |
| ML | scikit-learn (Ridge, RandomForest) |
| Data | yfinance, Pandas, NumPy, SciPy |

## License

MIT
