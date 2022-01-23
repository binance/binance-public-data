#!/usr/bin/env python

"""
  script to download klines.
  set the absoluate path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-kline.py

"""
import sys
from datetime import *
import pandas as pd
from binance_pandas_dataframe.enums import *

from binance_pandas_dataframe.utility import download_file, get_all_symbols, get_destination_dir, get_parser, get_start_end_date_objects, convert_to_date_object, \
    get_path,redirect_print
from pathlib import Path
from itertools import chain

# columns |Open time|Open|High|Low|Close|Volume|Close time|Quote asset volume|Number of trades|Taker buy base asset volume|Taker buy quote asset volume|Ignore|
# | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
# |1601510340000|4.15070000|4.15870000|4.15060000|4.15540000|539.23000000|1601510399999|2240.39860900|13|401.82000000|1669.98121300|0|

_kline_cols = ["Open_time_ms", "Open", "High", "Low", "Close", "Volume", "Close_time_ms", "Quote_asset_volume", "Number_of_trades", "Take_buy_base_asset_volume",
               "Taker buy quote asset volume", "Ignore"]

# for reoordering after we add interval and symbol in.  Open_time is not in the  list because it is the index.
_ordered_cols = ["Symbol", "Interval", "Open_time","Close_time", "Open", "High", "Low", "Close", "Volume", "Quote_asset_volume", "Number_of_trades", "Take_buy_base_asset_volume",
                 "Taker buy quote asset volume", "Ignore"]

def read_kline_csv(dl_file):
    df = pd.read_csv(
        dl_file, names=_kline_cols, index_col=None)
    for col in ["Open_time", "Close_time"]:
        df[col] = pd.to_datetime(
            df[col+"_ms"], unit="ms")
    df2 = df[["Open_time", "Close_time",
                "Open_time_ms", "Close_time_ms"]]
#                            df.set_index("Open_time", inplace=True)
    df["Interval"]=interval
    df["Symbol"]=symbol
    return df


def download_monthly_klines(trading_type, symbols, num_symbols, intervals,  start_year, end_year, folder, checksum):
    current = 0
    date_range = None

    # if start_date and end_date:
    #     date_range = start_date + " " + end_date

    # if not start_date:
    #     start_date = START_DATE
    # else:
    #     start_date = convert_to_date_object(start_date)

    # if not end_date:
    #     end_date = END_DATE
    # else:
    #     end_date = convert_to_date_object(end_date)

    print("Found {} symbols".format(num_symbols))
    interval_frames = []

    #current += 1  #perhaps this should go somewhere, something useless from original binance code

    #arrange years in reverse chronological order.
    print(f"\n start_year {start_year}  {dir(start_year)}")
    print(f"\n end_year {end_year}  {dir(end_year)}")
    years=list(range(end_year,start_year-1,-1))

    months=list(range(12,0,-1))
    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current +
              1, num_symbols, symbol))
        for interval in intervals:
            for year in years:
                for month in months:
                    current_date = convert_to_date_object(
                        '{}-{}-01'.format(year, month))
                    path = get_path(trading_type, "klines",
                                    "monthly", symbol, interval)
                    file_name = "{}-{}-{}-{}.zip".format(
                        symbol.upper(), interval, year, '{:02d}'.format(month))
                    dl_file = download_file(
                        path, file_name, date_range, folder)
                    print(".")
                    print(f"\nReading File {dl_file}\n")
                    try:  # ignore any exceptions that happen here, probably means there is no data for the interval.
                        df = read_kline_csv(dl_file)

                        print(f"\ndf\n{df}")
                        interval_frames.append(df)

                        if checksum == 1:
                            checksum_path = get_path(
                                trading_type, "klines", "monthly", symbol, interval)
                            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(
                                symbol.upper(), interval, year, '{:02d}'.format(month))
                            download_file(
                                checksum_path, checksum_file_name, date_range, folder)
                    except:
                        pass
    return interval_frames


def download_daily_klines(trading_type, symbols, num_symbols, intervals, year, month, folder, checksum):
    """Download daily klines for the given month"""
    current = 0
    date_range = None
    interval_frames = []

    # Get valid intervals for daily
    intervals = list(set(intervals) & set(DAILY_INTERVALS))
    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download daily {} klines ".format(current +
              1, num_symbols, symbol))
        for interval in intervals:
            for day in range(0,32):  #31 days in a month max
                try:
                    d=date(year, month, day)
                    path = get_path(trading_type, "klines",
                                    "daily", symbol, interval)
                    file_name = "{}-{}-{}.zip".format(
                        symbol.upper(), interval, d)
                    dl_file = download_file(
                        path, file_name, date_range, folder)
                    df = read_kline_csv(dl_file)

                    print(f"\ndf\n{df}")
                    interval_frames.append(df)

                    if checksum == 1:
                        checksum_path = get_path(
                            trading_type, "klines", "daily", symbol, interval)
                        checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(
                            symbol.upper(), interval, date)
                        download_file(
                            checksum_path, checksum_file_name, date_range, folder)
                except:
                    pass

        current += 1
        return interval_frames


def main():
    redirect_print()
    parser = get_parser('klines')
    print(f"sys.argv {sys.argv}")
    args = parser.parse_args(sys.argv[1:])

    if args.all_symbols:
        print("fetching all symbols from exchange")
        symbols = get_all_symbols(args.type)
        num_symbols = len(symbols)
    elif args.symbols:
        symbols = args.symbols
        num_symbols = len(symbols)
    else:
        print("No symbols specified")
        return 0

    print(f"\nStart year {args.start_year}")
    # if args.dates:
    #     dates = args.dates
    # else:
    #     dates = pd.date_range(end=datetime.today(),
    #                           periods=MAX_DAYS).to_pydatetime().tolist()
    # dates = [date.strftime("%Y-%m-%d") for date in dates]


    monthly_frames = download_monthly_klines(args.type, symbols, num_symbols, \
         args.intervals, args.start_year, END_YEAR,args.folder, args.checksum)

    print(f"\nMonthly frames {monthly_frames}")

    daily_frames = download_daily_klines(args.type,symbols,num_symbols,args.intervals,END_YEAR, END_DATE.month, args.folder,args.checksum)

    df_all = pd.concat(monthly_frames,ignore_index=True)
    df_all = df_all.reindex(columns=_ordered_cols)
    df_all = df_all.set_index(["Symbol","Interval","Open_time"])
    return df_all

        #download daily klines for the current month
        #too much trouble to exclude if the current year hasn't been requested.  
    
    #download_daily_klines(args.type, symbols, num_symbols, args.intervals, dates, args.startDate, args.endDate, args.folder, args.checksum)


if __name__ == "__main__":
    main()
