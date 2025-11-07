ThetaStrike — AI-Powered Options Pricing & Analytics Engine

ThetaStrike is a full-stack quantitative finance platform built using FastAPI and React, designed to evaluate, compare, and forecast European and American option premiums.
It combines mathematical pricing models (Black-Scholes and Binomial Tree) with machine learning prediction pipelines to forecast future stock prices, implied volatility, and option moneyness (ITM/OTM likelihood).

------------------------------------------------------------
Key Features
------------------------------------------------------------
- **Option Pricing Models**
  - European options priced using the Black–Scholes model
  - American options priced using a discrete binomial tree model
  - Compute current or future option premiums based on predicted stock price and time to maturity
- **Market Data Integration**
  - Fetch live stock data, option chains, and expiries using the yfinance API
  - Endpoints:
    - `/stock/{ticker}/price` — fetches OHLC + volume data
    - `/option/{ticker}/chain` — returns full option chain by expiry
    - `/option-price` — unified pricing endpoint
- **Machine Learning Engine**
  - ML module predicts future stock prices based on historical OHLC data
  - Regression models (XGBoost / LSTM / ARIMA) trained on past stock movements
  - Separate pipeline for implied volatility (IV) estimation using option chain history
  - Predicts probability of option expiring ITM/OTM based on ML forecasts
  - Integrated into backend `/evaluate-ml` endpoint for real-time predictions
- **Unified Backend API (FastAPI)**
  - RESTful API serving both pricing and ML predictions
  - Modular structure with separated math models, ML models, and market data logic
  - Fully documented endpoints available via `/docs`
  - Deployed on Render with CORS-enabled frontend access
- **Frontend Web Interface (React)**
  - Clean single-page dashboard built with React and plain CSS
  - Input fields for:
    - Market type (European / American)
    - Ticker symbol
    - Expiry date
    - Strike price
    - Option type (Call / Put)
    - Optional: future date for predicted premium
  - Displays both model-based price and AI-predicted premium trend


------------------------------------------------------------
Project Structure
-----------------

```
ThetaStrike/
│
├── Backend/                       FastAPI backend
│   ├── src/
│   │   ├── core/                  Pricing models (Black–Scholes, Binomial)
│   │   ├── apis/                  yfinance data fetchers & market endpoints
│   │   ├── pricing_engine/        Core evaluation wrapper
│   │   ├── ml_engine/             Machine learning models & training scripts
│   │   └── api_server.py          FastAPI entrypoint
│   ├── test/                      Unit tests for pricing and ML modules
│   └── requirements.txt           Production dependencies
│
├── Frontend/                      React frontend (Vite + CSS)
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── components/
│   │       └── OptionForm.js
│   └── index.html
│
└── README.txt                     Project documentation
```  

Project documentation


------------------------------------------------------------
Backend Setup
------------------------------------------------------------
1. Install dependencies:
   cd Backend
   pip install -r requirements.txt

2. Run FastAPI server:
   uvicorn src.api_server:app --reload

Backend runs at: http://127.0.0.1:8000
Interactive docs: http://127.0.0.1:8000/docs

------------------------------------------------------------
Frontend Setup
------------------------------------------------------------
1. Install dependencies:
   cd Frontend
   npm install

2. Run development server:
   npm run dev

Frontend runs at: http://localhost:5173

------------------------------------------------------------
Example API Usage
------------------------------------------------------------
Request:
```
GET /option-price?model=american&ticker=NVDA&expiry=2025-09-26&strike=190&option_type=call
Response:
{
  "ticker": "NVDA",
  "expiry": "2025-09-26",
  "strike": 190,
  "option_type": "call",
  "predict_date": "today",
  "model": "american",
  "premium": 35.42
}
```

------------------------------------------------------------
Frontend Features
------------------------------------------------------------
- Select European (Black–Scholes) or American (Binomial) model
- Enter ticker, expiry date, strike, call/put
- Optional: future date to predict premium
- Displays calculated premium from backend

------------------------------------------------------------
ML Workflow Overview
------------------------------------------------------------
- **Data Collection:** Historical price and option chain fetched via yfinance
- **Feature Engineering:**
  - Lagged returns, volatility, moving averages
  - Option greeks and moneyness ratio
- **Model Training:**
  - Regression for price prediction (XGBoost / LSTM)
  - Volatility forecast using rolling standard deviation or ML models
- **Prediction Engine:**
  - Predicts next-period stock price and implied volatility
  - Computes expected option premium under both forecasts
  - Outputs ITM/OTM classification

------------------------------------------------------------
Roadmap
------------------------------------------------------------
- **Phase 1 — Core MVP (Complete)**
  - FastAPI + React integration
  - Black-Scholes and Binomial models
  - yfinance live data endpoints
- **Phase 2 — ML Integration (In Progress)**
  - ML module to predict:
    - Future stock price
    - Implied volatility
    - ITM/OTM probability
  - Store training data and model weights locally
- **Phase 3 — SWE Scalability**
  - Add PostgreSQL database + caching
  - Background training jobs (Celery + Redis)
  - Dockerize for Render / AWS deployment
- **Phase 4 — Full Product**
  - User authentication
  - Saved watchlists
  - Mispricing dashboard (actual vs theoretical vs ML price)

------------------------------------------------------------
Tech Stack
------------------------------------------------------------
Layer                Technology
------------------------------------------------------------
Frontend             React (Vite, plain CSS)
Backend API          FastAPI (Python 3.10+)
Pricing Models       Black–Scholes, Binomial Tree
ML Models            XGBoost, scikit-learn, optional LSTM (TensorFlow)
Market Data          yfinance API
Data Libraries       NumPy, Pandas, SciPy
Hosting              Render (backend), Vercel (frontend)

------------------------------------------------------------
License
------------------------------------------------------------
MIT License — open source and free to modify.
