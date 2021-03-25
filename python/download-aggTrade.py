#!/usr/bin/env python

"""
  script to download aggTrades.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-aggTrade.py

"""

import os, sys, re
import json
from pathlib import Path
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from datetime import datetime
import pandas as pd


YEARS = ['2017', '2018', '2019', '2020', '2021']
MONTHS = list(range(1,13))
MAX_DAYS = 35

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
    print("\nfile already exists! {}".format(save_path))
    return
  
  # make the directory
  Path(get_destination_dir(path)).mkdir(parents=True, exist_ok=True)

  try:
    download_url = get_download_url(file_path)
    dl_file = urllib.request.urlopen(download_url)
    length = dl_file.getheader('content-length')
    if length:
      length = int(length)
      blocksize = max(4096,length//100)

    with open(save_path, 'wb') as out_file:
      dl_progress = 0
      print("\nFile Download: {}".format(save_path))
      while True:
        buf = dl_file.read(blocksize)   
        if not buf:
          break
        dl_progress += len(buf)
        out_file.write(buf)
        done = int(50 * dl_progress / length)
        sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50-done)) )    
        sys.stdout.flush()

  except urllib.error.HTTPError:
    print("\nFile not found: {}".format(download_url))
    pass

def match_date_regex(arg_value, pat=re.compile(r'\d{4}-\d{2}-\d{2}')):
  if not pat.match(arg_value):
    raise ArgumentTypeError
  return arg_value

def get_parser():
    parser = ArgumentParser(description=("This is a script to download historical aggTrades data"), formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-s', dest='symbols', nargs='+',
        help='single symbol or multiple symbols separated by space')
    parser.add_argument(
        '-y', dest='years', default=YEARS, nargs='+', choices=YEARS,
        help='single year or multiple years separated by space\n-y 2019 2021 means to download aggTrades from 2019 and 2021')
    parser.add_argument(
        '-m', dest='months', default=MONTHS,  nargs='+', type=int, choices=MONTHS,
        help='single month or multiple months separated by space\n-m 2 12 means to download aggTrades from feb and dec')
    parser.add_argument(
        '-d', dest='dates', nargs='+', type=match_date_regex,
        help='date to download in [YYYY-MM-DD] format\nsingle date or multiple dates separated by space\nDownload past 35 days if no argument is parsed')
    parser.add_argument(
        '-c', dest='checksum', default=0, type=int, choices=[0,1],
        help='1 to download checksum file, default 0')

    return parser

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

    download_monthly_aggTrades(symbols, num_symbols, args.years, args.months, args.checksum)
    if args.dates:
      dates = args.dates
    else:
      dates = pd.date_range(end = datetime.today(), periods = MAX_DAYS).to_pydatetime().tolist()
      dates = [date.strftime("%Y-%m-%d") for date in dates]
    download_daily_aggTrades(symbols, num_symbols, dates, args.checksum)
    
