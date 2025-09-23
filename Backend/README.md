ThetaStrike — Option Pricing Engine

ThetaStrike is a Python(Flask) + React project that allows you to evaluate European and American option premiums.
It uses Black–Scholes for European options and a binomial tree model for American options.
A FastAPI backend powers the pricing logic, while a React frontend provides a simple UI.

------------------------------------------------------------
Features
------------------------------------------------------------
- European option pricing via Black–Scholes model
- American option pricing via binomial tree model
- Fetch stock and option chain data using yfinance
- Predict option premiums at future dates and stock prices
- API endpoints exposed with FastAPI
- Frontend UI built with React (Vite) and plain CSS

------------------------------------------------------------
Project Structure
-----------------

project-root/
│
├── Backend/                 FastAPI backend
│   ├── src/
│   │   ├── core/            Pricing models (Black–Scholes, Binomial)
│   │   ├── apis/            yfinance data fetchers
│   │   ├── pricing_engine/  Evaluation wrapper
│   │   └── api_server.py    FastAPI entrypoint
│   └── test/                Unit tests
│
├── Frontend/                React frontend (Vite + CSS)
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── components/
│   │       └── OptionForm.js
│   └── index.html
│
└── README.txt               Project documentation


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
Frontend Setup (IN PROGRESS)
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

------------------------------------------------------------
Frontend Features
------------------------------------------------------------
- Select European (Black–Scholes) or American (Binomial) model
- Enter ticker, expiry date, strike, call/put
- Optional: future date to predict premium
- Displays calculated premium from backend

------------------------------------------------------------
Roadmap
------------------------------------------------------------
- Add ML model to predict stock prices and volatility
- Auto-populate expiries and strikes from option chain API
- Database caching for faster repeated queries
- Deployment (backend to Render/Heroku, frontend to Vercel/Netlify)

------------------------------------------------------------
License
------------------------------------------------------------
MIT License — free to use and modify.
