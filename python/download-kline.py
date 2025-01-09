#!/usr/bin/env python

"""
  script to download klines.
  set the absolute path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download-kline.py

"""
import sys
from datetime import *
import pandas as pd
from enums import *
from utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, \
    get_path
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_monthly_klines(trading_type, symbols, num_symbols, intervals, years, months, start_date, end_date, folder,
                            checksum):
    current = 0
    date_range = None

    if start_date and end_date:
        date_range = start_date + " " + end_date

    if not start_date:
        start_date = START_DATE
    else:
        start_date = convert_to_date_object(start_date)

    if not end_date:
        end_date = END_DATE
    else:
        end_date = convert_to_date_object(end_date)

    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current + 1, num_symbols, symbol))
        for interval in intervals:
            for year in years:
                for month in months:
                    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
                    if current_date >= start_date and current_date <= end_date:
                        path = get_path(trading_type, "klines", "monthly", symbol, interval)
                        file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))
                        download_file(path, file_name, date_range, folder)

                        if checksum == 1:
                            checksum_path = get_path(trading_type, "klines", "monthly", symbol, interval)
                            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year,
                                                                                   '{:02d}'.format(month))
                            download_file(checksum_path, checksum_file_name, date_range, folder)

        current += 1


# def download_daily_klines(trading_type, symbols, num_symbols, intervals, dates, start_date, end_date, folder, checksum):
#     current = 0
#     date_range = None
#
#     if start_date and end_date:
#         date_range = start_date + " " + end_date
#
#     if not start_date:
#         start_date = START_DATE
#     else:
#         start_date = convert_to_date_object(start_date)
#
#     if not end_date:
#         end_date = END_DATE
#     else:
#         end_date = convert_to_date_object(end_date)
#
#     #Get valid intervals for daily
#     intervals = list(set(intervals) & set(DAILY_INTERVALS))
#     print("Found {} symbols".format(num_symbols))
#
#     for symbol in symbols:
#         print("[{}/{}] - start download daily {} klines ".format(current + 1, num_symbols, symbol))
#         for interval in intervals:
#             for date in dates:
#                 current_date = convert_to_date_object(date)
#                 if current_date >= start_date and current_date <= end_date:
#                     path = get_path(trading_type, "klines", "daily", symbol, interval)
#                     file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)
#                     download_file(path, file_name, date_range, folder)
#
#                     if checksum == 1:
#                         checksum_path = get_path(trading_type, "klines", "daily", symbol, interval)
#                         checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)
#                         download_file(checksum_path, checksum_file_name, date_range, folder)
#
#         current += 1
def download_daily_klines(trading_type, symbols, num_symbols,
                          intervals, dates, start_date, end_date,
                          folder, checksum, max_workers=10):
    current = 0
    date_range = None

    if start_date and end_date:
        date_range = start_date + " " + end_date

    if not start_date:
        start_date = START_DATE
    else:
        start_date = convert_to_date_object(start_date)

    if not end_date:
        end_date = END_DATE
    else:
        end_date = convert_to_date_object(end_date)

    # Get valid intervals for daily
    intervals = list(set(intervals) & set(DAILY_INTERVALS))
    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download daily {} klines ".format(current + 1, num_symbols, symbol))

        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for interval in intervals:
                for date in dates:
                    current_date = convert_to_date_object(date)
                    if current_date >= start_date and current_date <= end_date:
                        # Submit the download task to the thread pool
                        futures.append(
                            executor.submit(download_file_task, trading_type, symbol, interval, date, date_range,
                                            folder, checksum))

            # Wait for all tasks to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error occurred while downloading: {e}")

        current += 1


def download_file_task(trading_type, symbol, interval, date, date_range, folder, checksum):
    path = get_path(trading_type, "klines", "daily", symbol, interval)
    file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)
    download_file(path, file_name, date_range, folder)

    if checksum == 1:
        checksum_path = get_path(trading_type, "klines", "daily", symbol, interval)
        checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)
        download_file(checksum_path, checksum_file_name, date_range, folder)


if __name__ == "__main__":
    parser = get_parser('klines')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
        print("fetching all symbols from exchange")
        symbols = get_all_symbols(args.type)
        num_symbols = len(symbols)
    else:
        symbols = args.symbols
        num_symbols = len(symbols)

    if args.dates:
        dates = args.dates
    else:
        period = convert_to_date_object(datetime.today().strftime('%Y-%m-%d')) - convert_to_date_object(
            PERIOD_START_DATE)
        dates = pd.date_range(end=datetime.today(), periods=period.days + 1).to_pydatetime().tolist()
        dates = [date.strftime("%Y-%m-%d") for date in dates]
        if args.skip_monthly == 0:
            download_monthly_klines(args.type, symbols, num_symbols, args.intervals, args.years, args.months,
                                    args.startDate, args.endDate, args.folder, args.checksum)
    if args.max_workers:
        max_workers = args.max_workers
    else:
        max_workers = 10
    if args.skip_daily == 0:
        download_daily_klines(args.type, symbols, num_symbols, args.intervals, dates, args.startDate, args.endDate,
                              args.folder, args.checksum, max_workers)
