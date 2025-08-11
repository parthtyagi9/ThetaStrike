import yfinance as yf
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.estimator import is_market_open

def fetch_option_data(ticker_symbol, expire_date, strike_price, option_type, ath):
    ticker = yf.ticker(ticker_symbol)

    current_price = ticker.fast_info["last_price"]
    current_price_ath  = ticker.history(period="1d", interval="1m", prepost=True)


    if ath == 0 or is_market_open:
        return current_price
    else:
        return current_price_ath


def trial():
    ticker_name = yf.Ticker("SPY")
    # print(ticker_name.fast_info["preMarketChange"])
    # print(ticker_name.history(period="1d", interval="1m", prepost=True).iloc[-1]["Close"])
    print(ticker_name.option_chain().puts.index.dtype)
    # calls_df = ticker_name.option_chain('2025-08-01').calls
    # print(calls_df)


print(trial())
