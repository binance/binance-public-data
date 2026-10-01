#!/usr/bin/env python3
"""
Binance COIN-M Futures Klines Downloader (Monthly)

Downloads monthly kline (candlestick) history from Binance COIN-M futures.

Features:
- Auto-detects available date range from the web
- Skips downloading if local data already exists
- Shows detailed progress (symbol, date, file size)
- Supports multiple time intervals

Examples:
    # Download with auto-detected date range and default intervals (recommended)
    python3 scripts/download-futures-cm-monthly-klines.py -s ADAUSD_PERP

    # Download for specific year/month range with default intervals
    python3 scripts/download-futures-cm-monthly-klines.py -s ADAUSD_PERP BTCUSD_PERP -y 2023 2024

    # Download with specific intervals
    python3 scripts/download-futures-cm-monthly-klines.py -s ADAUSD_PERP -i 1m 1h 1d

    # Download multiple symbols
    python3 scripts/download-futures-cm-monthly-klines.py -s ADAUSD_PERP BCHUSD_PERP

    # Specify custom output folder
    python3 scripts/download-futures-cm-monthly-klines.py -s ADAUSD_PERP -folder /data/binance
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_data_downloader.downloaders.kline_downloader import KlineDownloader
from binance_data_downloader.utils.logger_setup import setup_logger, log_level_from_string


def download_klines_monthly(
    symbols: list = None,
    intervals: list = None,
    years: list = None,
    months: list = None,
    folder: str = None,
    skip_existing: bool = True,
    log_level: str = 'INFO'
) -> int:
    """
    Download COIN-M futures klines monthly data.

    Args:
        symbols: List of trading symbols
        intervals: List of time intervals (None for default)
        years: List of years to download (None for default: 2020-current)
        months: List of months to download (None for all months)
        folder: Output folder
        skip_existing: Whether to skip existing files
        log_level: Logging level

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    logger = logging.getLogger("binance_data_downloader")
    trading_type = 'cm'

    # Set default intervals if not specified
    if not intervals:
        intervals = ["1m", "15m", "1h", "4h", "8h"]

    try:
        # Set default years if not specified
        if not years:
            current_year = datetime.now().year
            years = list(range(2020, current_year + 1))

        # Set default months if not specified
        if not months:
            months = list(range(1, 13))

        logger.info(f"Date range: {min(years)} to {max(years)}, months {min(months)}-{max(months)}")
        logger.info(f"Intervals: {', '.join(intervals)}")

        # Initialize downloader with 10 concurrent threads
        downloader = KlineDownloader(
            trading_type=trading_type,
            max_workers=10
        )
        logger.info(f"Using 10 threads for concurrent downloads")

        for symbol in symbols:
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing symbol: {symbol}")
            logger.info(f"{'='*70}")

            # Check local data range
            logger.info(f"Checking local data...")
            local_start, local_end = downloader.get_local_date_range(symbol, folder, time_period='monthly')

            if local_start and local_end:
                logger.info(f"Local data range: {local_start} to {local_end}")
                logger.info(f"Note: Will skip existing files during download")
            else:
                logger.info(f"No local data found, will download all files")

            # Download monthly data
            logger.info(f"Starting monthly download...")
            downloaded_count = downloader.download_monthly(
                symbols=[symbol],
                intervals=intervals,
                years=years,
                months=months,
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
        description='Binance COIN-M Futures Klines Downloader (Monthly)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-s', '--symbols',
        type=str,
        nargs='+',
        required=False,
        help='Trading symbols (e.g., ADAUSD_PERP BCHUSD_PERP). If not specified, downloads all available cm symbols.'
    )

    parser.add_argument(
        '-i', '--intervals',
        type=str,
        nargs='+',
        default=None,
        help='Kline intervals (e.g., 1m 15m 1h 4h 8h). Default: 1m 15m 1h 4h 8h'
    )

    parser.add_argument(
        '-y', '--years',
        type=int,
        nargs='+',
        default=None,
        help='Years to download (e.g., 2023 2024). Default: 2020 to current year'
    )

    parser.add_argument(
        '-m', '--months',
        type=int,
        nargs='+',
        choices=range(1, 13),
        default=None,
        metavar='MONTH',
        help='Months to download (1-12). Default: all months'
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

    logger.info("Binance COIN-M Futures Klines Downloader (Monthly)")
    logger.info(f"Market type: cm (COIN-M Futures)")
    logger.info(f"Symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    logger.info(f"Data type: MONTHLY")

    return download_klines_monthly(
        symbols=symbols,
        intervals=args.intervals,
        years=args.years,
        months=args.months,
        folder=args.folder,
        skip_existing=not args.no_skip_existing,
        log_level=args.log_level
    )


if __name__ == "__main__":
    sys.exit(main())
