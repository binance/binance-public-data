#!/usr/bin/env python

"""
  script to download aggTrades.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-aggTrade.py

"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from datetime import datetime
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser

def download_monthly_aggTrades(symbols, num_symbols, years, months, checksum):
  current = 0
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download monthly {} aggTrades ".format(current+1, num_symbols, symbol))
    for year in args.years:
      for month in args.months:
        path = "data/spot/monthly/aggTrades/{}/".format(symbol.upper())
        file_name = "{}-aggTrades-{}-{}.zip".format(symbol.upper(), year, '{:02d}'.format(month))
        download_file(path, file_name)

        if checksum == 1:
          checksum_path = "data/spot/monthly/aggTrades/{}/".format(symbol.upper())
          checksum_file_name = "{}-aggTrades-{}-{}.zip.CHECKSUM".format(symbol.upper(), year, '{:02d}'.format(month))
          download_file(checksum_path, checksum_file_name)
    
    current += 1

def download_daily_aggTrades(symbols, num_symbols, dates, checksum):
  current = 0
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download daily {} aggTrades ".format(current+1, num_symbols, symbol))
    for date in dates:
      path = "data/spot/daily/aggTrades/{}/".format(symbol.upper())
      file_name = "{}-aggTrades-{}.zip".format(symbol.upper(), date)
      download_file(path, file_name)

      if checksum == 1:
        checksum_path = "data/spot/daily/aggTrades/{}/".format(symbol.upper())
        checksum_file_name = "{}-aggTrades-{}.zip.CHECKSUM".format(symbol.upper(), date)
        download_file(checksum_path, checksum_file_name)

    current += 1

if __name__ == "__main__":
    parser = get_parser('aggTrades')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
      print("fetching all symbols from exchange")
      symbols = get_all_symbols()
      num_symbols = len(symbols)
    else:
      symbols = args.symbols
      num_symbols = len(symbols)
      print("fetching {} symbols from exchange".format(num_symbols))

    if args.dates:
      dates = args.dates
    else:
      dates = pd.date_range(end = datetime.today(), periods = MAX_DAYS).to_pydatetime().tolist()
      dates = [date.strftime("%Y-%m-%d") for date in dates]
      download_monthly_aggTrades(symbols, num_symbols, args.years, args.months, args.checksum)
    download_daily_aggTrades(symbols, num_symbols, dates, args.checksum)
    
