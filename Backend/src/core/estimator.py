from datetime import datetime
from zoneinfo import ZoneInfo

def is_market_open():
    now_et = datetime.now(ZoneInfo("America/New_York"))
    is_weekday = now_et.weekday() < 5
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    return is_weekday and market_open <= now_et <= market_close

print(is_market_open())