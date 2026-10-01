#!/usr/bin/env python3
"""
Check Funding Rate Data Range

This script checks the available data range for funding rate data from Binance.

Example:
    python3 scripts/check-funding-rate-range.py -t um -s BTCUSDT
    python3 scripts/check-funding-rate-range.py -t um -s BTCUSDT ETHUSDT
"""

import argparse
import logging
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_data_downloader.utils.data_explorer import DataExplorer
from binance_data_downloader.utils.logger_setup import setup_logger, log_level_from_string


def check_funding_rate_range(market: str, symbols: list, log_level: str = 'INFO') -> int:
    """
    Check the available data range for funding rate data.

    Args:
        market: Market type ('um' or 'cm')
        symbols: List of trading symbols
        log_level: Logging level

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Setup logging
    setup_logger(
        name="binance_data_downloader",
        level=log_level_from_string(log_level),
        log_file=None,
    )
    logger = logging.getLogger("binance_data_downloader")

    logger.info("Checking Funding Rate Data Range")
    logger.info(f"Market: {market.upper()}")
    logger.info(f"Symbols: {', '.join(symbols)}")
    logger.info("")

    explorer = DataExplorer()

    results = {}

    for symbol in symbols:
        logger.info(f"Checking {symbol}...")
        start_date, end_date = explorer.get_data_date_range_from_web(
            market=market,
            data_type='fundingRate',
            symbol=symbol,
            time_period='daily'
        )

        if start_date and end_date:
            results[symbol] = (start_date, end_date)
            logger.info(f"  ✓ Data range: {start_date} to {end_date}")
        else:
            results[symbol] = (None, None)
            logger.warning(f"  ✗ No data found")

    # Print summary
    logger.info("")
    logger.info("="*60)
    logger.info("Summary:")
    logger.info("="*60)

    for symbol, (start, end) in results.items():
        if start and end:
            logger.info(f"  {symbol:15s} | {start} to {end}")
        else:
            logger.info(f"  {symbol:15s} | No data available")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Check funding rate data range from Binance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-t', '--type',
        type=str,
        required=True,
        choices=['um', 'cm'],
        help='Market type: um (USD-M Futures) or cm (COIN-M Futures)'
    )

    parser.add_argument(
        '-s', '--symbols',
        type=str,
        nargs='+',
        required=True,
        help='Trading symbols (e.g., BTCUSDT ETHUSDT)'
    )

    parser.add_argument(
        '-log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    return check_funding_rate_range(
        market=args.type,
        symbols=args.symbols,
        log_level=args.log_level
    )


if __name__ == "__main__":
    sys.exit(main())
