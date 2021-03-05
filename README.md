# Binance Public Data

To help users download our public data easily, we've put all Kline, Trade, and AggTrade data for all pairs, month by month, online.


## What data is available

### SPOT

* `AggTrades`
* `Klines`
* `Trades`


#### AggTrades
The aggTrades is downloaded from `/api/v3/aggTrades` and the title for each column:

|Aggregate tradeId|Price|Quantity|First tradeId|Last tradeId|Timestamp|Was the buyer the maker|Was the trade the best price match|
| -- | -- | -- | -- | -- | -- | -- | -- |
|0|0.20000000|50.00000000|0|0|1608872400000|False|True|

#### Klines
The klines data is downloaded from `/api/v3/klines` and the title for each column in the kline data:

|Open time|Open|High|Low|Close|Volume|Close time|Quote asset volume|Number of trades|Taker buy base asset volume|Taker buy quote asset volume|Ignore|
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
|1601510340000|4.15070000|4.15870000|4.15060000|4.15540000|539.23000000|1601510399999|2240.39860900|13|401.82000000|1669.98121300|0|

#### Trades
The trades data is downloaded from `/api/v3/historicalTrades`, the title for each column in the trades data:
|trade Id| price| qty|quoteQty|time|isBuyerMaker|isBestMatch|
| -- | -- | -- | -- | -- | -- | -- |
|51175358|17.80180000|5.69000000|101.29224200|1583709433583|True|True|



### FUTURES
* USD-M Futures
* COIN-M Futures


## Where do I access it

The base url is `https://data.binance.vision` and you can use your browser to view and download the data.

### Klines

All symbols are supported, the file format is:<br/>
`<base_url>/data/spot/monthly/klines/<symbol_in_uppercase>/<interval>/<symbol_in_uppercase>-<interval>-<year>-<month>.zip`<br/><br/>
e.g. the url for BNBUSDT 1m klines for 2019-01 is:<br/>
`https://data.binance.vision/data/spot/monthly/klines/BNBUSDT/1m/BNBUSDT-1m-2019-01.zip`


#### Intervals

All intervals are supported: 
`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1mo`
- `1mo` is used instead of `1M` to supprt non-case sensitive file systems.

### Trades

All symbols are supported, the file format is:<br/>
`<base_url>/data/spot/monthly/trades/<symbol_in_uppercase>/<symbol_in_uppercase>-trades-<year>-<month>.zip`<br/><br/>
e.g. the url BNBUSDT trades in 2019-01 is:<br/>
`https://data.binance.vision/data/spot/monthly/trades/BNBUSDT/BNBUSDT-trades-2019-01.zip`

### AggTrades

This section will be updated when the data is uploaded.


## How to download programatically

```shell

# download a single file
curl -s "https://data.binance.vision/data/spot/monthly/klines/ADABKRW/1h/ADABKRW-1h-2020-08.zip" -o ADABKRW-1h-2020-08.zip
wget "https://data.binance.vision/data/spot/monthly/klines/ADABKRW/1h/ADABKRW-1h-2020-08.zip"
```

We will expand this section with more methods in the future.

There are additional helper scripts both in python and shell in their respective folders of this repository.

## CHECKSUM
Each zip file has a `.CHECKSUM` file together in the same folder to verify data integrity. 

To Check:

```shell
# From Linux, sha256sum -c <zip_file_name.CHECKSUM>
sha256sum -c BNBUSDT-1m-2021-01.zip.CHECKSUM

# From MacOS
shasum -a 256 -c BNBUSDT-1m-2021-01.zip.CHECKSUM
```


## I have an issue/question

Please open an issue [here](https://github.com/binance/binance-public-data/issues). 

## Licence
MIT
