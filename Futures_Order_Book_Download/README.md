# 1 Futures Orderbook Download

This document describes how to download the futures orderbook level 2 data via API.
For historical data on trades, klines and aggtrades (for both Futures and Spot), users can download directly from our public website. Please refer to this page: https://www.binance.com/en/landing/data  (**Note: You have to click "Apply for it", and fill the form to apply first.**)

Data update frequency: T+1; normally will be ready at UTC+0 4:00 am.

Three Data types are provided:
+ T_DEPTH: tick-by-tick order book (level 2). Directly fetched from our api, will have gaps.
+ S_DEPTH: order book snapshot (level 2); this is a temp data solution only for BTCUSDT at the moment.
+ T_DEPTH_BACKFILL: tick-by-tick order book (level 2). T_DEPTH backfilled with internal logs. Currently in beta. And has stopped producing since mid-July 2021, resume date TBD.  


## 1.1  Level 2 tick-by-tick order book data (T_DEPTH, T_DEPTH_BACKFILL)
#### 1.1.1  Data Schema



|field|desc|
|:-----|:-----|
|symbol|Both COIN-M and USDT-M futures symbol name are supported (queried through different symbol, for example: 'BTCUSDT', 'BTCUSD_200925')|
|time|Transaction time in timestamp. From 2020/07/01 to current date. For newly launched symbols , starting from the launch date.|
|first_update_id|-|
|last_update_id|-|
|pu|Last_update_id of previous row, to help exam completeness. Only applicable to Coin-Margined futures depth update (not orderbook snapshot).|
|side|a = ask (SELL order)<br>b = bid (BUY order)</br>|
|update_type|snap = used for order book snapshot only<br>set = set price level to current qty (not delta)<br>delta = qty change of the price level (delta)</br>|
|price|-|
|qty|-|



#### 1.1.2  Sample data

|symbol|timestamp|first_update_id|last_update_id|side|update_type|price|qty|
|:-----|:-----|:-----|:-----|:-----|:-----|:-----|:-----|
|BTCUSDT|1593647999921|39538108420|39538108420|a|set|9235.09|0|
|BTCUSDT|1593647999933|39538108444|39538108444|a|set|9236.04|0.852|
|BTCUSDT|1593647999954|39538108472|39538108472|b|set|9219.67|0|
|BTCUSDT|1593647999983|39538108497|39538108497|a|set|9236.04|0.912|
|BTCUSDT|1593647999983|39538108498|39538108498|a|set|9235.11|0|





#### 1.1.3  Data Completeness
For Coin-Margined futures, a small part of the datasets is missing. You can use the "pu" column to check the detail which will be like below:
+ 2020.09.27 lost 18 seconds
+ 2020.10.24 lost 121 seconds


## 1.2  Level 2 order book snapshot (S_DEPTH)
Currently only BTCUSDT at around 1s (1000 ms) interval with 20 price levels is supported. A small part of the data is missing, and will be back filled in the future.

      

    

#  2 How to download the Historical Futures Order Book level 2 Data via API

## 2.1 General Info 
+ The data download API is part of the Binance API (https://binance-docs.github.io/apidocs/spot/en/#general-api-information).
+ For how to use it, you may find info there with more examples, especially SIGNED Endpoint security as in https://binance-docs.github.io/apidocs/spot/en/#signed-trade-user_data-and-margin-endpoint-security
+ For accessing Futures data, the API account also needs to open a Futures account.
 


## 2.2 How to obtain the futures order book data programatically

#### Get download ID and download link for Futures Historic Order Book Data

+ An example python script is provided to demonstrate how to download the Historical Future Order Book level 2 Data via API.
+ Make sure that your API key has been whitelisted to access the data.
+ Specify the following arguments to request the download ID and the download link:

|Argument|Type|Mandatory|Description|
|:-----|:-----|:-----|:-----|
|symbol|STRING|YES|example:'BTCUSDT', 'BTCUSD_200925'|
|startTime|LONG|YES|Timestamp in ms, INCLUSIVE|
|endTime|LONG|YES|Timestamp in ms, INCLUSIVE|
|dataType|ENUM|YES|Three types: <br>"T_DEPTH",<br>"S_DEPTH",<br>"T_DEPTH_BACKFILL"</br>|
|recvWindow|LONG|NO|specify the number of milliseconds after timestamp the request is valid for. If recvWindow is not sent, it defaults to 5000.|
|timestamp|LONG|YES|current timestamp|


#### Notes:
+ For bulk data download, it may take hours to generate the download link. 
+ The range between startTime and endTime has to be smaller than 7 days.
+ For dataType info (available symbol and time range), please refer to part1 "dataset description".


