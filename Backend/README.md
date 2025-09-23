ThetaStrike — Option Pricing Engine

ThetaStrike is a Python(Flask) + React project that allows you to evaluate European and American option premiums.
It uses Black–Scholes for European options and a binomial tree model for American options.
A FastAPI backend powers the pricing logic, while a React frontend provides a simple UI.
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
