from datetime import *
START_YEAR=2017
INTERVALS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"]
DAILY_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
TRADING_TYPE = ["spot", "um", "cm"]
MONTHS = list(range(1,13))
MAX_DAYS = 35
BASE_URL = 'https://data.binance.vision/'
END_DATE = datetime.date(datetime.now())
END_YEAR = date.today().year
#YEARS = [f"{year}" for year in range(START_YEAR, 1+END_YEAR)]
YEARS = list(range(START_YEAR,1+END_YEAR))
START_DATE = date(int(START_YEAR), MONTHS[0], 1)
