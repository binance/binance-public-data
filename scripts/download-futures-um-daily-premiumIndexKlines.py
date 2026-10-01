#!/usr/bin/env python3
"""
Binance USD-M Futures Daily Premium Index Klines Downloader

Optimized script for downloading daily premium index klines history from Binance USD-M futures.
This script downloads DAILY premium index klines data.

Features:
- Hardcoded for USD-M Futures (um) market
- Auto-detects available date range from the web
- Skips downloading if local data already exists
- Shows detailed progress (symbol, date, file size)
- Uses 10 threads for concurrent downloads
- Supports multiple intervals (default: 1m, 15m, 1h, 4h, 8h)

Examples:
    # Download with auto-detected date range and default intervals (recommended)
    python3 scripts/download-futures-um-daily-premiumIndexKlines.py -s BTCUSDT

    # Download for specific date range
    python3 scripts/download-futures-um-daily-premiumIndexKlines.py -s BTCUSDT -startDate 2024-01-01 -endDate 2024-12-31

    # Download with specific intervals
    python3 scripts/download-futures-um-daily-premiumIndexKlines.py -s BTCUSDT -i 1h 4h 1d

    # Download multiple symbols
    python3 scripts/download-futures-um-daily-premiumIndexKlines.py -s BTCUSDT ETHUSDT

    # Specify custom output folder
    python3 scripts/download-futures-um-daily-premiumIndexKlines.py -s BTCUSDT -folder /data/binance
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_data_downloader.downloaders.premium_index_downloader import PremiumIndexDownloader
from binance_data_downloader.utils.data_explorer import DataExplorer
from binance_data_downloader.utils.logger_setup import setup_logger, log_level_from_string


def download_premium_index_klines_daily(
    symbols: list = None,
    intervals: list = None,
    start_date: str = None,
    end_date: str = None,
    folder: str = None,
    skip_existing: bool = True,
    log_level: str = 'INFO'
) -> int:
    """
    Download premium index klines daily data with smart features.

    Args:
        symbols: List of trading symbols
        intervals: List of kline intervals (default: ["1m", "15m", "1h", "4h", "8h"])
        start_date: Start date in YYYY-MM-DD format (None for default: 2020-01-01)
        end_date: End date in YYYY-MM-DD format (None for default: current date)
        folder: Output folder
        skip_existing: Whether to skip existing files
        log_level: Logging level

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    logger = logging.getLogger("binance_data_downloader")

    try:
        # Set default intervals if not specified
        if not intervals:
            intervals = ["1m", "15m", "1h", "4h", "8h"]

        # Set default date range if not specified
        if not start_date:
            start_date = "2020-01-01"

        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"Intervals: {', '.join(intervals)}")
        logger.info(f"Date range: {start_date} to {end_date}")

        # Initialize downloader with 10 concurrent threads
        downloader = PremiumIndexDownloader(
            trading_type='um',
            max_workers=10
        )
        logger.info(f"Using 10 threads for concurrent downloads")

        # Generate date list from start_date to end_date
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime("%Y-%m-%d"))
            current = (current - datetime(1970, 1, 1)).days + 1
            current = datetime.fromtimestamp(current * 86400)

        logger.info(f"Total dates to download: {len(date_list)}")

        for symbol in symbols:
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing symbol: {symbol}")
            logger.info(f"{'='*70}")

            # Check local data range
            logger.info(f"Checking local data...")
            local_start, local_end = downloader.get_local_date_range(symbol, folder, time_period='daily')

            if local_start and local_end:
                logger.info(f"Local data range: {local_start} to {local_end}")
                logger.info(f"Note: Will skip existing files during download")
            else:
                logger.info(f"No local data found, will download all files")

            # Download daily data
            logger.info(f"Starting daily download...")
            downloaded_count = downloader.download_daily(
                symbols=[symbol],
                intervals=intervals,
                dates=date_list,
                folder=folder,
                download_checksum=False,
                verify_checksum=False,
                skip_existing=skip_existing
            )

            if downloaded_count > 0:
                logger.info(f"Successfully downloaded {downloaded_count} files for {symbol}")
            else:
                logger.info(f"All files already exist for {symbol} (no new downloads)")

        logger.info(f"\n{'='*70}")
        logger.info(f"All downloads completed!")
        logger.info(f"{'='*70}")
        return 0

    except Exception as e:
        logger.exception(f"Download failed: {e}")
        return 1


def main():
    """Main entry point."""
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    default_output_folder = os.path.join(project_root, 'data')

    parser = argparse.ArgumentParser(
        description='Binance USD-M Futures Daily Premium Index Klines Downloader\n'
                    'Downloads DAILY premium index klines data.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-s', '--symbols',
        type=str,
        nargs='+',
        required=False,
        help='Trading symbols (e.g., BTCUSDT ETHUSDT). If not specified, downloads all available USD-M futures symbols.'
    )

    parser.add_argument(
        '-i', '--intervals',
        type=str,
        nargs='+',
        default=None,
        help='Kline intervals (e.g., 1m 15m 1h 4h 8h). Default: 1m 15m 1h 4h 8h'
    )

    parser.add_argument(
        '-startDate',
        type=str,
        default=None,
        help='Start date in YYYY-MM-DD format (default: 2020-01-01)'
    )

    parser.add_argument(
        '-endDate',
        type=str,
        default=None,
        help='End date in YYYY-MM-DD format (default: current date)'
    )

    parser.add_argument(
        '-folder',
        type=str,
        default=default_output_folder,
        help=f'Output folder (default: {default_output_folder})'
    )

    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Download all files even if they exist locally'
    )

    parser.add_argument(
        '-log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger(
        name="binance_data_downloader",
        level=log_level_from_string(args.log_level),
        log_file=None,
    )
    logger = logging.getLogger("binance_data_downloader")

    # Fetch symbols if not specified
    symbols = args.symbols
    if not symbols:
        logger.info("No symbols specified, fetching all USD-M futures symbols from exchange...")
        temp_downloader = PremiumIndexDownloader(trading_type='um', max_workers=10)
        symbols = temp_downloader.fetch_symbols('um')
        logger.info(f"Found {len(symbols)} symbols")

    logger.info("Binance USD-M Futures Daily Premium Index Klines Downloader")
    logger.info(f"Market type: um (USD-M Futures)")
    logger.info(f"Symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    logger.info(f"Data type: DAILY")
    logger.info(f"Intervals: {', '.join(args.intervals) if args.intervals else '1m, 15m, 1h, 4h, 8h'}")

    return download_premium_index_klines_daily(
        symbols=symbols,
        intervals=args.intervals,
        start_date=args.startDate,
        end_date=args.endDate,
        folder=args.folder,
        skip_existing=not args.no_skip_existing,
        log_level=args.log_level
    )


if __name__ == "__main__":
    sys.exit(main())
