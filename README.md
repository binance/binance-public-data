# Binance Public Data

To help users download our public data easily, we've put all Kline, Trade, and AggTrade data for all pairs, month by month, online.

**Note:** AggTrade data is still being prepared.

## What data is available

SPOT

* `Klines`
* `Trades`

FUTURES data is **not available** as of this time.

## Where do I access it

The base url is `https://data.binance.vision` and you can use your browser to view and download the data.

### Klines

All symbols are supported, the file format is:<br/>
`<base_url>/data/spot/klines/<symbol_in_uppercase>/<interval>/<symbol_in_uppercase>-<interval>-<year>-<month>.zip`<br/><br/>
e.g. the url for BNBUSDT 1m klines for 2019-01 is:<br/>
`https://data.binance.vision/data/spot/klines/BNBUSDT/1m/BNBUSDT-1m-2019-01.zip`


#### Intervals

All intervals are supported: 
`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1mo`
- `1mo` is used instead of `1M` to supprt non-case sensitive file systems.

### Trades

All symbols are supported, the file format is:<br/>
`<base_url>/data/spot/trades/<symbol_in_uppercase>/<symbol_in_uppercase>-trades-<year>-<month>.zip`<br/><br/>
e.g. the url BNBUSDT trades in 2019-01 is:<br/>
`https://data.binance.vision/data/spot/trades/BNBUSDT/BNBUSDT-trades-2019-01.zip`

### AggTrades

This section will be updated when the data is uploaded.


## How to download programatically

```shell

# download a single file
curl -s "https://data.binance.vision/data/spot/klines/ADABKRW/1h/ADABKRW-1h-2020-08.zip" -o ADABKRW-1h-2020-08.zip
wget "https://data.binance.vision/data/spot/klines/ADABKRW/1h/ADABKRW-1h-2020-08.zip"
```

We will expand this section with more methods in the future.

There are additional helper scripts both in python and shell in their respective folders of this repository.

## I have an issue/question

Please open an issue [here](https://github.com/binance/binance-public-data/issues). 

## Licence
MIT
