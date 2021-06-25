## Installing the dependencies

`pip install -r requirements.txt`

## Running the scripts

`export STORE_DIRECTORY=<your desired path>`

This will configure the default storing directory of the downloaded data. This can be 
overwritten <br/> by setting an argument(example given below). 

`python3 download-kline.py` <br/>
`python3 download-trade.py` <br/>
`python3 download-aggTrade.py` 

Downloads all monthly and daily(for past 35 days) klines/trades/aggTrades of all intervals(applicable to klines only) and symbols.

`python3 download-kline.py --help` 

This will show the arguments that can be parsed to the scripts which can be used to configure download options.

### Running with arguments

| Argument        | Explanation |         
| --------------- | ---------------- |
| -h              | show help messages| 
| -s              | Single symbol or multiple symbols separated by space | 
| -y              | Single year or multiple years separated by space| 
| -m              | Single month or multiple months separated by space | 
| -d              | single date or multiple dates separated by space    | 
| -startDate      | Starting date to download in [YYYY-MM-DD] format    | 
| -endDate        | Ending date to download in [YYYY-MM-DD] format     | 
| -folder         | Directory to store the downloaded data    | 
| -c              | 1 to download checksum file, default 0       | 
| -i              | single kline interval or multiple intervals separated by space      |

e.g download ETHUSDT BTCUSDT BNBBUSD kline of 1 week interval from year 2020, month of Feb and Dec with CHECKSUM file:<br/>
`python3 download-kline.py -s ETHUSDT BTCUSDT BNBBUSD -i 1w -y 2020 -m 02 12 -c 1`

eg. download ETHUSDT kline from 2020-01-01 to 2021-02-02 to directory /Users/bob/Binance:<br/>
`python3 download-kline.py -s ETHUSDT -startDate 2020-01-01 -endDate 2021-02-02 -folder '/Users/bob/Binance'`