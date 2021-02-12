#!/usr/bin/env python

"""
  script to download klines.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-kline.py

"""

import os
import json
from pathlib import Path
import urllib.request


YEARS = ['2017', '2018', '2019', '2020']
INTERVALS = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"]

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
    print("file already existed! {}".format(save_path))
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

if __name__ == "__main__":
    print("fetching all symbols from exchange")
    symbols = get_all_symbols()
    all = len(symbols)

    current = 0
    print("Found {} symbols".format(all))

    for symbol in symbols:
      print("[{}/{}] - start download {} klines ".format(current+1, all, symbol))
      for interval in INTERVALS:
        for year in YEARS:
          for month in list(range(1, 13)):
            path = "data/spot/klines/{}/{}/".format(symbol.upper(), interval)
            file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))
            download_file(path, file_name)
      
      current += 1
