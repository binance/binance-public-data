#!/usr/bin/env python3
"""
Binance COIN-M Futures Daily Klines Downloader

Optimized script for downloading daily klines history from Binance COIN-M Futures.
This script downloads DAILY klines (candlestick) data.

Features:
- Hardcoded for COIN-M Futures (cm) market
- Downloads DAILY data only
- Auto-skips existing files
- Shows detailed progress (symbol, date, file size)
- Uses 10 concurrent threads for faster downloads
- Supports multiple kline intervals

Examples:
    # Download for specific symbol and date range with default intervals
    python3 scripts/download-futures-cm-daily-klines.py -s BTCUSD_PERP -startDate 2023-01-01 -endDate 2023-12-31

    # Download with custom intervals
    python3 scripts/download-futures-cm-daily-klines.py -s BTCUSD_PERP -i 1h 4h -startDate 2023-01-01 -endDate 2023-12-31

    # Download multiple symbols
    python3 scripts/download-futures-cm-daily-klines.py -s BTCUSD_PERP ETHUSD_PERP -startDate 2023-01-01 -endDate 2023-12-31

    # Download with auto-detected symbols (all cm symbols)
    python3 scripts/download-futures-cm-daily-klines.py -startDate 2023-01-01 -endDate 2023-12-31

    # Specify custom output folder
    python3 scripts/download-futures-cm-daily-klines.py -s BTCUSD_PERP -folder /data/binance -startDate 2023-01-01 -endDate 2023-12-31
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_data_downloader.downloaders.kline_downloader import KlineDownloader
from binance_data_downloader.utils.logger_setup import setup_logger, log_level_from_string


def download_klines_daily(
    symbols: list,
    intervals: list,
    start_date: str,
    end_date: str,
    folder: str = None,
    skip_existing: bool = True,
    log_level: str = 'INFO'
) -> int:
    """
    Download COIN-M Futures daily klines data.

    Args:
        symbols: List of trading symbols
        intervals: List of kline intervals
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        folder: Output folder
        skip_existing: Whether to skip existing files
        log_level: Logging level

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    logger = logging.getLogger("binance_data_downloader")

    try:
        logger.info(f"Date range: {start_date} to {end_date}")
        logger.info(f"Market type: COIN-M Futures (cm)")
        logger.info(f"Intervals: {', '.join(intervals)}")

        # Initialize downloader with 10 concurrent threads
        downloader = KlineDownloader(
            trading_type='cm',
            max_workers=10
        )
        logger.info(f"Using 10 threads for concurrent downloads")

        # Generate date list
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_list = [(start + timedelta(days=i)).strftime('%Y-%m-%d')
                     for i in range((end - start).days + 1)]

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
        description='Binance COIN-M Futures Daily Klines Downloader\n'
                    'Downloads DAILY klines (candlestick) data for COIN-M Futures.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-s', '--symbols',
        type=str,
        nargs='+',
        required=False,
        help='Trading symbols (e.g., BTCUSD_PERP ETHUSD_PERP). If not specified, downloads all available cm symbols.'
    )

    parser.add_argument(
        '-i', '--intervals',
        type=str,
        nargs='+',
        default=['1m', '15m', '1h', '4h', '8h'],
        help='Kline intervals (e.g., 1m 15m 1h 4h 8h). Default: 1m 15m 1h 4h 8h'
    )

    parser.add_argument(
        '-startDate',
        type=str,
        required=True,
        help='Start date in YYYY-MM-DD format (e.g., 2023-01-01)'
    )

    parser.add_argument(
        '-endDate',
        type=str,
        required=True,
        help='End date in YYYY-MM-DD format (e.g., 2023-12-31)'
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
        logger.info("No symbols specified, fetching all cm symbols from exchange...")
        temp_downloader = KlineDownloader(trading_type='cm', max_workers=10)
        symbols = temp_downloader.fetch_symbols('cm')
        logger.info(f"Found {len(symbols)} symbols")

    logger.info("Binance COIN-M Futures Daily Klines Downloader")
    logger.info(f"Market type: cm (COIN-M Futures)")
    logger.info(f"Symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    logger.info(f"Data type: DAILY klines")
    logger.info(f"Intervals: {', '.join(args.intervals)}")

    return download_klines_daily(
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
