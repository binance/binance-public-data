#!/usr/bin/env python3
"""Binance Spot AggTrades Downloader (Monthly)"""
import argparse, logging, os, sys
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from binance_data_downloader.downloaders.agg_trade_downloader import AggTradeDownloader
from binance_data_downloader.utils.logger_setup import setup_logger, log_level_from_string

def download(symbols, years, months, folder, skip, log_level):
    logger = logging.getLogger("binance_data_downloader")
    try:
        if not years: years = list(range(2020, datetime.now().year + 1))
        if not months: months = list(range(1, 13))
        logger.info(f"Date range: {min(years)}-{max(years)}, months {min(months)}-{max(months)}")
        downloader = AggTradeDownloader('spot', max_workers=10)
        logger.info("Using 10 threads")
        for s in symbols:
            logger.info(f"\n{'='*70}\nProcessing: {s}\n{'='*70}")
            local_start, local_end = downloader.get_local_date_range(s, folder, 'monthly')
            if local_start: logger.info(f"Local: {local_start} to {local_end}")
            count = downloader.download_monthly([s], None, years, months, folder, False, False, skip)
            logger.info(f"Downloaded: {count} files")
        return 0
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1

def main():
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    default_output_folder = os.path.join(project_root, 'data')

    p = argparse.ArgumentParser()
    p.add_argument('-s', nargs='+', help='Symbols')
    p.add_argument('-y', type=int, nargs='+', help='Years')
    p.add_argument('-m', type=int, nargs='+', choices=range(1,13), help='Months')
    p.add_argument('-folder', default=default_output_folder, help=f'Output folder (default: {default_output_folder})')
    p.add_argument('--no-skip-existing', action='store_true')
    p.add_argument('-log-level', default='INFO', choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'])
    a = p.parse_args()
    setup_logger("binance_data_downloader", level=log_level_from_string(a.log_level), log_file=None)
    logger = logging.getLogger("binance_data_downloader")
    symbols = a.symbols
    if not symbols:
        temp = AggTradeDownloader('spot', 10)
        symbols = temp.fetch_symbols('spot')
        logger.info(f"Found {len(symbols)} symbols")
    logger.info(f"Binance Spot AggTrades (Monthly)\nSymbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    return download(symbols, a.years, a.months, a.folder, not a.no_skip_existing, a.log_level)

if __name__ == "__main__":
    sys.exit(main())
