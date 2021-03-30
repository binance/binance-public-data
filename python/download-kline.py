#!/usr/bin/env python

"""
  script to download klines.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-kline.py

"""
import sys
from datetime import datetime
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser


def download_monthly_klines(symbols, num_symbols, intervals, years, months, checksum):
  current = 0
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download monthly {} klines ".format(current+1, num_symbols, symbol))
    for interval in args.intervals:
      for year in args.years:
        for month in args.months:
          path = "data/spot/monthly/klines/{}/{}/".format(symbol.upper(), interval)
          file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))
          download_file(path, file_name)

          if checksum == 1:
            checksum_path = "data/spot/monthly/klines/{}/{}/".format(symbol.upper(), interval)
            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year, '{:02d}'.format(month))
            download_file(checksum_path, checksum_file_name)
    
    current += 1

def download_daily_klines(symbols, num_symbols, intervals, dates, checksum):
  current = 0
  #Get valid intervals for daily
  intervals = list(set(intervals) & set(DAILY_INTERVALS))
  print("Found {} symbols".format(num_symbols))
  for symbol in symbols:
    print("[{}/{}] - start download daily {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for date in dates:
        path = "data/spot/daily/klines/{}/{}/".format(symbol.upper(), interval)
        file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)
        download_file(path, file_name)

        if checksum == 1:
          checksum_path = "data/spot/daily/klines/{}/{}/".format(symbol.upper(), interval)
          checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)
          download_file(checksum_path, checksum_file_name)

    current += 1

if __name__ == "__main__":
    parser = get_parser('klines')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
      print("fetching all symbols from exchange")
      symbols = get_all_symbols()
      num_symbols = len(symbols)
    else:
      symbols = args.symbols
      num_symbols = len(symbols)

    
    if args.dates:
      dates = args.dates
    else:
      dates = pd.date_range(end = datetime.today(), periods = MAX_DAYS).to_pydatetime().tolist()
      dates = [date.strftime("%Y-%m-%d") for date in dates]
      download_monthly_klines(symbols, num_symbols, args.intervals, args.years, args.months, args.checksum)
    download_daily_klines(symbols, num_symbols, args.intervals, dates, args.checksum)
    
