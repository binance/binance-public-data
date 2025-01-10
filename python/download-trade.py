#!/usr/bin/env python3

"""
Enhanced script to download trades.
Set the absolute path destination folder for STORE_DIRECTORY, and run

e.g. STORE_DIRECTORY=/data/ ./download-trade.py

New features:
- Multithreading for faster downloads
- Progress bar for better visibility
- Improved error handling and logging
- Rate limiting to avoid overwhelming the server
- Automatic retries for failed downloads
- CSV export option for downloaded data summary
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.exceptions import RequestException
from tqdm import tqdm
import time
import logging
import csv
from enums import *
from utility import download_file, get_all_symbols, get_parser, get_start_end_date_objects, convert_to_date_object, get_path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
RATE_LIMIT = 0.5  # seconds between requests

def download_with_retry(path, file_name, date_range, folder, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            download_file(path, file_name, date_range, folder)
            time.sleep(RATE_LIMIT)  # Rate limiting
            return True
        except RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to download {file_name} after {max_retries} attempts")
                return False
        time.sleep(2 ** attempt)  # Exponential backoff

def download_monthly_trades(trading_type, symbols, num_symbols, years, months, start_date, end_date, folder, checksum):
    tasks = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for symbol in symbols:
            for year in years:
                for month in months:
                    current_date = convert_to_date_object(f'{year}-{month}-01')
                    if start_date <= current_date <= end_date:
                        path = get_path(trading_type, "trades", "monthly", symbol)
                        file_name = f"{symbol.upper()}-trades-{year}-{month:02d}.zip"
                        tasks.append(executor.submit(download_with_retry, path, file_name, f"{start_date} {end_date}", folder))

                        if checksum:
                            checksum_path = get_path(trading_type, "trades", "monthly", symbol)
                            checksum_file_name = f"{file_name}.CHECKSUM"
                            tasks.append(executor.submit(download_with_retry, checksum_path, checksum_file_name, f"{start_date} {end_date}", folder))

    return [task.result() for task in tqdm(as_completed(tasks), total=len(tasks), desc="Downloading monthly trades")]

def download_daily_trades(trading_type, symbols, num_symbols, dates, start_date, end_date, folder, checksum):
    tasks = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for symbol in symbols:
            for date in dates:
                current_date = convert_to_date_object(date)
                if start_date <= current_date <= end_date:
                    path = get_path(trading_type, "trades", "daily", symbol)
                    file_name = f"{symbol.upper()}-trades-{date}.zip"
                    tasks.append(executor.submit(download_with_retry, path, file_name, f"{start_date} {end_date}", folder))

                    if checksum:
                        checksum_path = get_path(trading_type, "trades", "daily", symbol)
                        checksum_file_name = f"{file_name}.CHECKSUM"
                        tasks.append(executor.submit(download_with_retry, checksum_path, checksum_file_name, f"{start_date} {end_date}", folder))

    return [task.result() for task in tqdm(as_completed(tasks), total=len(tasks), desc="Downloading daily trades")]

def export_summary(symbols, start_date, end_date, monthly_results, daily_results):
    summary_file = "download_summary.csv"
    with open(summary_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Symbol", "Start Date", "End Date", "Monthly Downloads", "Daily Downloads", "Total Downloads"])
        
        for symbol in symbols:
            monthly_count = sum(1 for result in monthly_results if result)
            daily_count = sum(1 for result in daily_results if result)
            total_count = monthly_count + daily_count
            writer.writerow([symbol, start_date, end_date, monthly_count, daily_count, total_count])
    
    logger.info(f"Download summary exported to {summary_file}")

if __name__ == "__main__":
    parser = get_parser('trades')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:
        logger.info("Fetching all symbols from exchange")
        symbols = get_all_symbols(args.type)
        num_symbols = len(symbols)
    else:
        symbols = args.symbols
        num_symbols = len(symbols)
        logger.info(f"Fetching {num_symbols} symbols from exchange")

    start_date, end_date = get_start_end_date_objects(args.startDate, args.endDate)

    if args.dates:
        dates = args.dates
    else:
        dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d").tolist()

    monthly_results = []
    daily_results = []

    if args.skip_monthly == 0:
        monthly_results = download_monthly_trades(args.type, symbols, num_symbols, args.years, args.months, start_date, end_date, args.folder, args.checksum)

    if args.skip_daily == 0:
        daily_results = download_daily_trades(args.type, symbols, num_symbols, dates, start_date, end_date, args.folder, args.checksum)

    export_summary(symbols, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), monthly_results, daily_results)

    logger.info("Download completed successfully!")
