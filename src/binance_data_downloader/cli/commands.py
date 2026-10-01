"""
Commands

This module provides command execution functions for the CLI.
"""

import logging
import random
import sys
from typing import List, Optional

import pandas as pd

from ..cli.argument_parser import parse_args
from ..config.config_loader import ConfigLoader, load_config
from ..core.checksum_verifier import ChecksumVerifier
from ..core.data_type_config import DataType, get_supported_data_types
from ..core.retry_handler import RetryHandler
from ..downloaders.agg_trade_downloader import AggTradeDownloader
from ..downloaders.book_ticker_downloader import BookTickerDownloader
from ..downloaders.depth_downloader import DepthDownloader
from ..downloaders.funding_rate_downloader import FundingRateDownloader
from ..downloaders.index_price_downloader import IndexPriceDownloader
from ..downloaders.kline_downloader import KlineDownloader
from ..downloaders.liquidation_snapshot_downloader import LiquidationSnapshotDownloader
from ..downloaders.mark_price_downloader import MarkPriceDownloader
from ..downloaders.option_downloader import OptionDownloader
from ..downloaders.premium_index_downloader import PremiumIndexDownloader
from ..downloaders.trade_downloader import TradeDownloader
from ..utils.date_utils import (
    convert_to_date_object,
    generate_date_range,
    get_default_end_date,
    get_default_start_date,
)
from ..utils.logger_setup import setup_logger, log_level_from_string
from ..utils.progress_tracker import MultiProgressTracker, ProgressTracker


# Downloader registry
DOWNLOADER_CLASSES = {
    'klines': KlineDownloader,
    'trades': TradeDownloader,
    'aggTrades': AggTradeDownloader,
    'indexPriceKlines': IndexPriceDownloader,
    'markPriceKlines': MarkPriceDownloader,
    'premiumIndexKlines': PremiumIndexDownloader,
    'fundingRate': FundingRateDownloader,
    'liquidationSnapshot': LiquidationSnapshotDownloader,
    'bookTicker': BookTickerDownloader,
    'depth': DepthDownloader,
    'option': OptionDownloader,
}


def execute_download_command(
    trading_type: str,
    data_type: str,
    symbols: Optional[List[str]] = None,
    intervals: Optional[List[str]] = None,
    years: Optional[List[str]] = None,
    months: Optional[List[int]] = None,
    dates: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    folder: Optional[str] = None,
    download_checksum: bool = False,
    verify_checksum: bool = False,
    skip_monthly: bool = False,
    skip_daily: bool = False,
    max_workers: int = 10,
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
) -> int:
    """
    Execute a download command for a single data type.

    Args:
        trading_type: Market type ('spot', 'um', or 'cm')
        data_type: Type of data to download
        symbols: List of symbols (None = all symbols)
        intervals: List of intervals (for klines)
        years: List of years
        months: List of months
        dates: List of specific dates
        start_date: Start date filter
        end_date: End date filter
        folder: Output directory
        download_checksum: Whether to download checksum files
        verify_checksum: Whether to verify checksums
        skip_monthly: Whether to skip monthly files
        skip_daily: Whether to skip daily files
        max_workers: Number of worker threads
        log_level: Logging level
        log_file: Log file path

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Setup logging
    setup_logger(
        name="binance_data_downloader",
        level=log_level_from_string(log_level),
        log_file=log_file,
    )
    logger = logging.getLogger("binance_data_downloader")

    try:
        # Get downloader class
        downloader_class = DOWNLOADER_CLASSES.get(data_type)
        if not downloader_class:
            logger.error(f"Unknown data type: {data_type}")
            return 1

        # Initialize downloader
        downloader = downloader_class(
            trading_type=trading_type,
            max_workers=max_workers,
        )

        # Get symbols
        if not symbols:
            logger.info(f"Fetching all {trading_type} symbols from exchange")
            symbols = downloader.fetch_symbols(trading_type)

            # For options, if API returns empty, use common option symbols
            if not symbols and trading_type == 'option':
                logger.warning("Could not fetch option symbols from API")
                logger.info("Options data requires specific option symbols (format: BTC-YYMMDD-STRIKE-C or -P)")
                logger.info("Example: BTC-240301-50000-C (Call) or BTC-240301-50000-P (Put)")
                logger.info("You will need to specify symbols with -s parameter")
                logger.info("For now, using example symbol - download will likely fail")
                # Use a placeholder - user should specify actual option symbols
                symbols = ['BTC-240301-50000-C']  # Example option symbol
                logger.info(f"Using example option symbol: {symbols[0]}")
            elif not symbols:
                logger.warning("No symbols found for this market")
                return 1

            random.shuffle(symbols)
            logger.info(f"Found {len(symbols)} symbols")

        logger.info(f"Starting download for {len(symbols)} symbols")

        # Calculate total number of files to download
        total_files = 0

        # Count monthly files (only if data type supports monthly)
        if not skip_monthly and downloader.data_type_spec.supports_monthly:
            intervals_count = len(intervals) if intervals else (1 if not downloader.supports_intervals() else 0)
            years_count = len(years) if years else 6  # Default years range
            months_count = len(months) if months else 12
            total_files += len(symbols) * max(1, intervals_count) * years_count * months_count

        # Count daily files
        if not skip_daily and downloader.data_type_spec.supports_daily:
            dates_list = dates
            if not dates_list:
                start = convert_to_date_object(start_date) if start_date else get_default_start_date()
                end = convert_to_date_object(end_date) if end_date else get_default_end_date()
                dates_list = generate_date_range(start, end)
            total_files += len(symbols) * len(dates_list)

        # Setup progress tracker
        progress = ProgressTracker(
            total_items=total_files,
            show_bar=True,
            show_statistics=True
        )

        # Download monthly files
        if not skip_monthly:
            logger.info("Starting monthly downloads")
            downloader.download_monthly(
                symbols=symbols,
                intervals=intervals,
                years=years,
                months=months,
                start_date=start_date,
                end_date=end_date,
                folder=folder,
                download_checksum=download_checksum,
                verify_checksum=verify_checksum,
                progress_tracker=progress,
            )

        # Generate date range for daily downloads
        if not dates and not skip_daily:
            start = convert_to_date_object(start_date) if start_date else get_default_start_date()
            end = convert_to_date_object(end_date) if end_date else get_default_end_date()
            dates = generate_date_range(start, end)

        # Download daily files
        if not skip_daily:
            logger.info("Starting daily downloads")
            downloader.download_daily(
                symbols=symbols,
                intervals=intervals,
                dates=dates,
                start_date=start_date,
                end_date=end_date,
                folder=folder,
                download_checksum=download_checksum,
                verify_checksum=verify_checksum,
                progress_tracker=progress,
            )

        # Finish progress tracking
        progress.finish(show_summary=True)

        logger.info("Download completed")
        return 0

    except Exception as e:
        logger.exception(f"Download failed: {e}")
        return 1


def execute_multi_download_command(
    trading_type: str,
    data_types: Optional[List[str]] = None,
    all_data: bool = False,
    **kwargs
) -> int:
    """
    Execute download command for multiple data types.

    Args:
        trading_type: Market type
        data_types: List of data types to download
        all_data: Download all supported data types
        **kwargs: Additional arguments passed to execute_download_command

    Returns:
        Exit code
    """
    logger = logging.getLogger("binance_data_downloader")

    # Determine which data types to download
    if all_data:
        data_types = [dt.value for dt in get_supported_data_types(trading_type)]
        logger.info(f"Downloading all {len(data_types)} supported data types for {trading_type}")
    elif not data_types:
        data_types = ['klines']  # Default to klines only

    # Download each data type
    multi_tracker = MultiProgressTracker(show_summary=True)

    for data_type in data_types:
        logger.info(f"Starting download for data type: {data_type}")

        exit_code = execute_download_command(
            trading_type=trading_type,
            data_type=data_type,
            **kwargs
        )

        if exit_code == 0:
            logger.info(f"Successfully completed download for {data_type}")
        else:
            logger.error(f"Failed to download {data_type}")

    # Show aggregate summary
    multi_tracker.show_aggregate_summary()

    return 0


def main(argv: Optional[List[str]] = None, parser_type: str = 'klines'):
    """
    Main entry point for CLI commands.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])
        parser_type: Type of parser to use

    Returns:
        Exit code
    """
    # Parse arguments
    args = parse_args(argv, parser_type)

    # Load config file if specified
    if args.config:
        config = load_config(args.config)
        # Apply config defaults where args not provided
        # ... (config merging logic)

    # Determine if multi-download
    if parser_type == 'download-all':
        return execute_multi_download_command(
            trading_type=args.type,
            data_types=getattr(args, 'data_types', None),
            all_data=getattr(args, 'all_data', False),
            symbols=args.symbols,
            intervals=getattr(args, 'intervals', None),
            years=args.years,
            months=args.months,
            dates=getattr(args, 'dates', None),
            start_date=args.startDate,
            end_date=args.endDate,
            folder=args.folder,
            download_checksum=args.checksum == 1,
            verify_checksum=getattr(args, 'verify_checksum', 0) == 1,
            skip_monthly=args.skip_monthly == 1,
            skip_daily=args.skip_daily == 1,
            max_workers=args.max_workers,
            log_level=args.log_level,
            log_file=args.log_file,
        )
    else:
        # Determine data type from parser type
        data_type_map = {
            'klines': 'klines',
            'trades': 'trades',
            'aggTrades': 'aggTrades',
            'fundingRate': 'fundingRate',
        }
        data_type = data_type_map.get(parser_type, parser_type)

        return execute_download_command(
            trading_type=args.type,
            data_type=data_type,
            symbols=args.symbols,
            intervals=getattr(args, 'intervals', None),
            years=args.years,
            months=args.months,
            dates=getattr(args, 'dates', None),
            start_date=args.startDate,
            end_date=args.endDate,
            folder=args.folder,
            download_checksum=args.checksum == 1,
            verify_checksum=getattr(args, 'verify_checksum', 0) == 1,
            skip_monthly=args.skip_monthly == 1,
            skip_daily=args.skip_daily == 1,
            max_workers=args.max_workers,
            log_level=args.log_level,
            log_file=args.log_file,
        )
