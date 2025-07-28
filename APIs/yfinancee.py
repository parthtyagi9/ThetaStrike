import yfinance as yf
import datetime
import json


def fetch_option_data(ticker_symbol, expire_date, strike_price, option_type):
    ticker = yf.ticker(ticker_symbol)

    current_price = ticker.fast_info["last_price"]


def trial():
    ticker_name = yf.Ticker("PLTR")
    # print(ticker_name.fast_info["last_price"])
    # print(ticker_name.option_chain(ticker_name.options[0]).puts)
    calls_df = ticker_name.option_chain('2025-08-01').calls
    calls_json = calls_df.to_dict(orient='records')
    print(json.dumps(calls_json, indent=2))


print(trial())