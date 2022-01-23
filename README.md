# Overview

binance_pandas_dataframe collects the historical data from 
[https://data.binance.vision](https://data.binance.vision) and builds Pandas dataframes from them
for use in Python.

The code was forked from 
[https://github.com/binance/binance-public-data](https://github.com/binance/binance-public-data), and the logic to build
the  Pandas dataframe was added.  

If you want to process data in a tool other than Python, such as R, Julia, or excel, you can use [pandas_dataframe_convert](https://pypi.org/project/pandas_dataframe_convert/)
to convert the dataframes produced by binance_pandas_dataframe to 'pkl', 'ftr', 'json', 'xlsx', 'csv', 'md', 'latex', or 'parquet'.

# Status

Currently only klines work.

# Installing 

## Installing from PyPi
`pip install binance_pandas_dataframes`  

## Installing from your git clone.

Flit is used to build the python package for installation with pip.  Flit will call pip as required.

This is the best way to do it.  In windows, do this from an adminstrator powershell 
for the symlink permissions.   

`flit install --symlink`

or you can install it this way, you will have to uninstall with pip and reinstall with flit for every change in a source file.
`flit install`



# Running the scripts

The scripts are installed in your python Scripts folder which should be in your path.

`export STORE_DIRECTORY=<your desired path>`

This will configure the default storing directory of the downloaded data. This can be 
overwritten <br/> by setting an argument(example given below). 

`download_kline` <br/>
`download_trade` <br/>
`download_aggTrade` 

Downloads all monthly and daily(for past 35 days) klines/trades/aggTrades of all intervals(applicable to klines only) and symbols.

`download_kline --help` 

This will show the arguments that can be parsed to the scripts which can be used to configure download options.

usage: download_kline [-h] [-s SYMBOLS [SYMBOLS ...]] [-a ALL_SYMBOLS [ALL_SYMBOLS ...]] [-y {2017,2018,2019,2020,2021,2022}] [-folder FOLDER] [-c {0,1}] [-t {spot,um,cm}] [-o OFILE] [--stdout] -i {1m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1mo}
                      [{1m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1mo} ...]

This is a script to download historical klines data

optional arguments:
  -h, --help            show this help message and exit
  -s SYMBOLS [SYMBOLS ...]
                        Single symbol or multiple symbols separated by space
  -a ALL_SYMBOLS [ALL_SYMBOLS ...]
                        download all symbols. because you can.
  -y {2017,2018,2019,2020,2021,2022}
                        Single year to start, read all klines data until today
  -folder FOLDER        Directory to store the downloaded data
  -c {0,1}              1 to download checksum file, default 0
  -t {spot,um,cm}       Valid trading types: ['spot', 'um', 'cm']
  -o OFILE              file for pandas dataframe.  Recommend using the .pkl extension.
                                        if you want another format for analyzing in R, excel, etc use
                                        dataframe_convert.

  --stdout              write the dataframe to stdandard output.  usueful if using a shell pipeline.  you can pipe output to
                              dataframe_convert  if you want a format for use in  excel, R, etc.

  -i {1m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1mo} [{1m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1mo} ...]
                        single kline interval or multiple intervals separated by space
                        -i 1m 1w means to download klines interval of 1minute and 1week



e.g.
`download_kline.cmd  -y 2021  -s ETHUSDT -o test.pkl `
`dataframe_convert  -i test.pkl -o test.csv` 

  to download to test.pkl and to create a csv as well

