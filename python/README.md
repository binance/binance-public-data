## Installing the dependencies

`pip install -r requirements.txt`

## Running the scripts

`export STORE_DIRECTORY=<your desired path>`

This will configure the default storing directory of the downloaded data. This can be 
overwritten <br/> by setting an argument(example given below). 

### Download klines
`python3 download-kline.py -t <market_type>` <br/>

Running this command will download all available monthly and daily **spot**, **USD-M Futures** or **COIN-M Futures** kline data for all symbols and intervals. 

#### Running with arguments

These are the available arguments that can be used when running `download-kline.py`<br>
Some arguments come with a default value if not declared.

| Argument        | Explanation | Default | Mandatory |      
| :---------------: | ---------------- | :----------------: | :----------------: |
| -t              | Market type: **spot**, **um** (USD-M Futures), **cm** (COIN-M Futures) | spot | Yes |
| -s              | Single **symbol** or multiple **symbols** separated by space | All symbols | No |
| -i              | single kline **interval** or multiple **intervals** separated by space      | All intervals | No |
| -y              | Single **year** or multiple **years** separated by space| All available years | No |
| -m              | Single **month** or multiple **months** separated by space | All available months | No |
| -d              | single **date** or multiple **dates** separated by space    | All available dates | No |
| -startDate      | **Starting date** to download in [YYYY-MM-DD] format    | - | No |
| -endDate        | **Ending date** to download in [YYYY-MM-DD] format     | - | No |
| -skip-monthly   | 1 to skip downloading of monthly data | 0 | No |
| -skip-daily     | 1 to skip downloading of daily data | 0 | No |
| -folder         | **Directory** to store the downloaded data    | Current directory | No |
| -c              | 1 to download **checksum file** | 0 | No |
| -h              | show help messages| - | No |

#### Example

e.g download ETHUSDT BTCUSDT BNBBUSD spot kline of 1 week interval from year 2020, month of Feb and Dec with CHECKSUM file:<br/>
`python3 download-kline.py -t spot -s ETHUSDT BTCUSDT BNBBUSD -i 1w -y 2020 -m 02 12 -c 1`

e.g download all symbols' daily USD-M futures kline of 1 minute interval from 2021-01-01 to 2021-02-02:
`python3 download-kline.py -t um -i 1m -skip-monthly 1 -startDate 2021-01-01 -endDate 2021-02-02`

### Download trades

`python3 download-trade.py -t <market_type>` <br/>

Running this command will download all available monthly and daily **spot**, **USD-M Futures** or **COIN-M Futures** trade data for all symbols.

#### Running with arguments

These are the available arguments that can be used when running `download-trade.py`<br>
Some arguments come with a default value if not declared.

| Argument        | Explanation | Default | Mandatory |       
| :---------------: | ---------------- | :----------------: | :----------------: |
| -t              | Market type: **spot**, **um** (USD-M Futures), **cm** (COIN-M Futures) | spot | Yes |
| -s              | Single **symbol** or multiple **symbols** separated by space | All symbols | No |
| -y              | Single **year** or multiple **years** separated by space| All available years | No |
| -m              | Single **month** or multiple **months** separated by space | All available months | No |
| -d              | single **date** or multiple **dates** separated by space    | All available dates | No |
| -startDate      | **Starting date** to download in [YYYY-MM-DD] format    | - | No |
| -endDate        | **Ending date** to download in [YYYY-MM-DD] format     | - | No |
| -skip-monthly   | 1 to skip downloading of monthly data | 0 | No |
| -skip-daily     | 1 to skip downloading of daily data | 0 | No |
| -folder         | **Directory** to store the downloaded data    | Current directory | No |
| -c              | 1 to download **checksum file** | 0 | No |
| -h              | show help messages| - | No |

#### Example

e.g download ETHUSDT BTCUSDT BNBBUSD spot trades from year 2020, month of Feb and Dec with CHECKSUM file:<br/>
`python3 download-trade.py -t spot -s ETHUSDT BTCUSDT BNBBUSD -y 2020 -m 02 12 -c 1`

e.g download all symbols' daily USD-M futures trades from 2021-01-01 to 2021-02-02:
`python3 download-trade.py -t um -skip-monthly 1 -startDate 2021-01-01 -endDate 2021-02-02`

### Download aggTrades

`python3 download-aggTrade.py -t <market_type> ` <br/>

Running this command will download all available monthly and daily **spot**, **USD-M Futures** or **COIN-M Futures** aggregated trades data for all symbols.

#### Running with arguments

These are the available arguments that can be used when running `download-aggTrade.py`<br>
Some arguments come with a default value if not declared.

| Argument        | Explanation | Default | Mandatory |       
| :---------------: | ---------------- | :----------------: | :----------------: |
| -t              | Market type: **spot**, **um** (USD-M Futures), **cm** (COIN-M Futures) | spot | Yes |
| -s              | Single **symbol** or multiple **symbols** separated by space | All symbols | No |
| -y              | Single **year** or multiple **years** separated by space| All available years | No |
| -m              | Single **month** or multiple **months** separated by space | All available months | No |
| -d              | single **date** or multiple **dates** separated by space    | All available dates | No |
| -startDate      | **Starting date** to download in [YYYY-MM-DD] format    | - | No |
| -endDate        | **Ending date** to download in [YYYY-MM-DD] format     | - | No |
| -skip-monthly   | 1 to skip downloading of monthly data | 0 | No |
| -skip-daily     | 1 to skip downloading of daily data | 0 | No |
| -folder         | **Directory** to store the downloaded data    | Current directory | No |
| -c              | 1 to download **checksum file** | 0 | No |
| -h              | show help messages| - | No |

#### Example

e.g download ETHUSDT BTCUSDT BNBBUSD spot aggTrades from year 2020, month of Feb and Dec with CHECKSUM file:<br/>
`python3 download-aggTrade.py -t spot -s ETHUSDT BTCUSDT BNBBUSD -y 2020 -m 02 12 -c 1`

e.g download all symbols' daily USD-M futures aggTrades from 2021-01-01 to 2021-02-02:
`python3 download-aggTrade.py -t um -skip-monthly 1 -startDate 2021-01-01 -endDate 2021-02-02`


### Futures-Only Data 

The 3 scripts below are only used for futures klines data.

`python3 download-futures-indexPriceKlines.py -t <market_type>` <br/>
`python3 download-futures-markPriceKlines.py -t <market_type>` <br/>
`python3 download-futures-premiumPriceKlines.py -t <market_type>` 

#### Running with arguments

These are the available arguments that can be used when running the scripts.<br>
**`-t`, type,  is a mandatory argument which consist of 2 different futures type: `um`, `cm`**. Some arguments come with a default value if not declared.

| Argument        | Explanation | Default | Mandatory |      
| :---------------: | ---------------- | :----------------: | :----------------: |
| -t              | Market type: **um** (USD-M Futures), **cm** (COIN-M Futures)| - | Yes |
| -s              | Single **symbol** or multiple **symbols** separated by space | All symbols | No |
| -i              | single kline **interval** or multiple **intervals** separated by space      | All intervals | No |
| -y              | Single **year** or multiple **years** separated by space| All available years | No |
| -m              | Single **month** or multiple **months** separated by space | All available months | No |
| -d              | single **date** or multiple **dates** separated by space    | All available dates | No |
| -startDate      | **Starting date** to download in [YYYY-MM-DD] format    | - | No |
| -endDate        | **Ending date** to download in [YYYY-MM-DD] format     | - | No |
| -skip-monthly   | 1 to skip downloading of monthly data | 0 | No |
| -skip-daily     | 1 to skip downloading of daily data | 0 | No |
| -folder         | **Directory** to store the downloaded data    | Current directory | No |
| -c              | 1 to download **checksum file** | 0 | No |
| -h              | show help messages| - | No |

e.g download Futures BTCUSDT USD-M indexPriceKlines
`python3 download-futures-indexPriceKlines.py -t um -s BTCUSDT`

e.g download ETHUSDT BTCUSDT BNBUSDT USD-M markPriceKlines of 1 week from year 2020, month of Feb and Dec with CHECKSUM file:<br/>
`python3 download-futures-markPriceKlines.py -t um -s ETHUSDT BTCUSDT BNBUSDT -i 1w -y 2020 -m 02 12 -c 1`

e.g download all symbols' daily COIN-M premiumPriceKlines of 1 minute interval from 2021-01-01 to 2021-02-02:
`python3 download-futures-premiumPriceKlines.py -t cm -skip-monthly 1 -i 1m  -startDate 2021-01-01 -endDate 2021-02-02`
