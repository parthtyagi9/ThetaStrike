import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import pandas as pd

from src.apis.yfinancee import get_stock_data, get_option_chain_by_expiry, get_iv
from src.pricing_engine.evaluate import EvaluationParams, evaluate_option_price


def test_stock_data():
    df = get_stock_data("AAPL", start_date="2024-01-01")
    print("✅ Stock data fetched:", df.tail(3))


def test_option_chain():
    expiry = "2025-01-17"
    chain = get_option_chain_by_expiry("AAPL", expiry=expiry)
    print(f"✅ Option chain for AAPL {expiry}:")
    print(chain.head())


def test_get_iv():
    iv = get_iv("AAPL", "2025-01-17", 150, "call")
    print(f"✅ IV for AAPL 150C Jan 2025: {iv:.2%}")


def test_evaluate_option():
    # Example: Evaluate a European call at strike 150, expiry Jan 2025
    expiry = "2025-01-17"
    today = datetime.today()
    expiry_date = pd.to_datetime(expiry)
    T_total = (expiry_date - today).days / 365.0

    # Use IV from market
    sigma = get_iv("AAPL", expiry, 150, "call")

    params = EvaluationParams(
        model="european",
        option_type="call",
        S_future=175,     # pretend predicted stock price
        K=150,
        T_total=T_total,
        t_elapsed=0.25,  # assume 3 months have passed
        r=0.05,
        sigma=sigma,
    )
    price = evaluate_option_price(params)
    print(f"✅ Predicted premium (European Call): {price:.2f}")


if __name__ == "__main__":
    test_stock_data()
    test_option_chain()
    test_get_iv()
    test_evaluate_option()
