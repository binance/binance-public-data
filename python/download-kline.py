#!/usr/bin/env python

"""
  script to download klines.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-kline.py

"""

import os, sys
import json
from pathlib import Path
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime
import pandas as pd


YEARS = ['2017', '2018', '2019', '2020', '2021']
#YEARS = ['2021']
INTERVALS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"]

MONTHS = list(range(1,13))
MAX_DAYS = 35
#INTERVALS = ["1h"]

BASE_URL = 'https://data.binance.vision/'

def get_destination_dir(file_url):
  store_directory = os.environ.get('STORE_DIRECTORY')
  if not store_directory:
    store_directory = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(store_directory, file_url)

def get_download_url(file_url):
    return "{}{}".format(BASE_URL, file_url)

def get_all_symbols():
  response = urllib.request.urlopen("https://api.binance.com/api/v3/exchangeInfo").read()
  return list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))

def download_file(path, file_name):
  file_path = "{}{}".format(path, file_name)
  save_path = get_destination_dir(file_path)

  if os.path.exists(save_path):
    print("file already exists! {}".format(save_path))
    return
  
  # make the directory
  Path(get_destination_dir(path)).mkdir(parents=True, exist_ok=True)

  try:
    download_url = get_download_url(file_path)
    with urllib.request.urlopen(download_url) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())
            print("File Download: {}".format(save_path))
  except urllib.error.HTTPError:
    print("File not found: {}".format(download_url))
    pass

def get_parser():
    parser = ArgumentParser(description=("This is a script to download historical kline data"), formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-s', '--symbol', dest='symbols', nargs='+',
        help='single symbol or multiple symbols separated by space')
    parser.add_argument(
        '-i', '--interval', dest='intervals', default=INTERVALS, nargs='+', choices=INTERVALS,
        help='single kline interval or multiple intervals separated by space\n-i 1m 1w means to download klines interval of 1minute and 1week')
    parser.add_argument(
        '-y', '--year', dest='years', default=YEARS, nargs='+', choices=YEARS,
        help='single year or multiple years separated by space\n-y 2019 2021 means to download klines from 2019 and 2021')
    parser.add_argument(
        '-m', '--month', dest='months', default=MONTHS,  nargs='+', type=int, choices=MONTHS,
        help='single month or multiple months separated by space\n-m 2 12 means to download klines from feb and dec')
    parser.add_argument(
        '-d', '--days', dest='days', default=MAX_DAYS, type=int, choices=range(1,36),
        help='past number of <DAYS> of klines to download (inclusive of current day, Max 35 days)\nwill not download if argument is not parsed')
    parser.add_argument(
        '-c', '--checksum', dest='checksum', default=0, type=int, choices=[0,1],
        help='1 to download checksum file, default 0')

    return parser

def download_monthly_klines(symbols, num_symbols, intervals, years, months):
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
    
    current += 1

def download_daily_klines(symbols, num_symbols, intervals, days):
  current = 0
  print("Found {} symbols".format(num_symbols))

  for symbol in symbols:
    print("[{}/{}] - start download daily {} klines ".format(current+1, num_symbols, symbol))
    for interval in intervals:
      for day in days:
        path = "data/spot/daily/klines/{}/{}/".format(symbol.upper(), interval)
        file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, day.strftime("%Y-%m-%d"))
        download_file(path, file_name)

    current += 1

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
      print("fetching all symbols from exchange")
      symbols = get_all_symbols()
      num_symbols = len(symbols)

    else:
      symbols = args.symbols
      num_symbols = len(symbols)
      print("fetching {} symbols from exchange".format(num_symbols))

    download_monthly_klines(symbols, num_symbols, args.intervals, args.years, args.months)
  
    days = pd.date_range(end = datetime.today(), periods = args.days).to_pydatetime().tolist()
    download_daily_klines(symbols, num_symbols, args.intervals, days)
    
