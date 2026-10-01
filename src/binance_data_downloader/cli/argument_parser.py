"""
Argument Parser

This module provides command-line argument parsing for the downloader.
"""

import argparse
import re
import sys
from typing import List, Optional


# Valid intervals for klines
VALID_INTERVALS = [
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"
]

# Valid daily intervals (subset of all intervals)
VALID_DAILY_INTERVALS = [
    "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"
]

# Valid trading types
VALID_TRADING_TYPES = ["spot", "um", "cm", "option"]

# Valid years
VALID_YEARS = ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']

# Valid data types
VALID_DATA_TYPES = [
    "klines", "trades", "aggTrades",
    "indexPriceKlines", "markPriceKlines", "premiumIndexKlines",
    "fundingRate", "liquidationSnapshot", "bookTicker", "depth", "option"
]


def match_date_regex(arg_value: str) -> str:
    """
    Validate date format (YYYY-MM-DD).

    Args:
        arg_value: Date string to validate

    Returns:
        The validated date string

    Raises:
        ArgumentTypeError: If date format is invalid
    """
    pat = re.compile(r'\d{4}-\d{2}-\d{2}')
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError(f"Invalid date format: {arg_value}. Use YYYY-MM-DD")
    return arg_value


def create_base_parser(description: str) -> argparse.ArgumentParser:
    """
    Create base argument parser with common arguments.

    Args:
        description: Parser description

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        '-t', '--type',
        dest='type',
        required=True,
        choices=VALID_TRADING_TYPES,
        help='Market type:\n'
             '  spot  - Spot trading\n'
             '  um    - USD-M Futures (USDT-margined)\n'
             '  cm    - COIN-M Futures (coin-margined)\n'
             '  option - Options market'
    )

    # Symbol selection
    parser.add_argument(
        '-s', '--symbols',
        dest='symbols',
        nargs='+',
        help='Trading symbols to download (e.g., BTCUSDT ETHUSDT)\n'
             'If not specified, downloads all available symbols'
    )

    # Date filtering
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '-y', '--years',
        dest='years',
        default=VALID_YEARS,
        nargs='+',
        choices=VALID_YEARS,
        help='Years to download (default: all available years)\n'
             'Example: -y 2023 2024'
    )
    date_group.add_argument(
        '-startDate',
        dest='startDate',
        type=match_date_regex,
        help='Start date in YYYY-MM-DD format\n'
             'Use with -endDate for date range filtering'
    )
    date_group.add_argument(
        '-d', '--dates',
        dest='dates',
        nargs='+',
        type=match_date_regex,
        help='Specific dates to download (YYYY-MM-DD format)\n'
             'Example: -d 2023-01-01 2023-01-15'
    )

    parser.add_argument(
        '-endDate',
        dest='endDate',
        type=match_date_regex,
        help='End date in YYYY-MM-DD format\n'
             'Use with -startDate for date range filtering'
    )

    parser.add_argument(
        '-m', '--months',
        dest='months',
        default=list(range(1, 13)),
        nargs='+',
        type=int,
        choices=range(1, 13),
        metavar='MONTH',
        help='Months to download (1-12, default: all months)\n'
             'Example: -m 1 6 12'
    )

    # Output options
    parser.add_argument(
        '-folder', '--folder',
        dest='folder',
        help='Output directory for downloaded files\n'
             '(overrides STORE_DIRECTORY environment variable)'
    )

    # Download options
    parser.add_argument(
        '-skip-monthly',
        dest='skip_monthly',
        default=0,
        type=int,
        choices=[0, 1],
        metavar='0|1',
        help='Skip monthly files (default: 0)\n'
             'Use 1 to skip monthly downloads'
    )

    parser.add_argument(
        '-skip-daily',
        dest='skip_daily',
        default=0,
        type=int,
        choices=[0, 1],
        metavar='0|1',
        help='Skip daily files (default: 0)\n'
             'Use 1 to skip daily downloads'
    )

    # Checksum options
    parser.add_argument(
        '-c', '--checksum',
        dest='checksum',
        default=0,
        type=int,
        choices=[0, 1],
        metavar='0|1',
        help='Download .CHECKSUM files (default: 0)\n'
             'Use 1 to enable checksum download'
    )

    parser.add_argument(
        '-verify-checksum',
        dest='verify_checksum',
        default=0,
        type=int,
        choices=[0, 1],
        metavar='0|1',
        help='Verify checksums after download (default: 0)\n'
             'Requires -c 1. Use 1 to enable verification'
    )

    # Performance options
    parser.add_argument(
        '-max-workers',
        dest='max_workers',
        type=int,
        default=10,
        metavar='N',
        help='Maximum number of download threads (default: 10)'
    )

    # Logging options
    parser.add_argument(
        '-log-level',
        dest='log_level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '-log-file',
        dest='log_file',
        help='Log file path (default: logs/download.log)'
    )

    # Config file option
    parser.add_argument(
        '--config',
        dest='config',
        help='Path to configuration file (YAML format)\n'
             'Command-line arguments override config file settings'
    )

    return parser


def create_kline_parser() -> argparse.ArgumentParser:
    """Create parser for kline downloads."""
    parser = create_base_parser(
        "Download kline (candlestick) data from Binance public data"
    )

    parser.add_argument(
        '-i', '--intervals',
        dest='intervals',
        default=VALID_INTERVALS,
        nargs='+',
        choices=VALID_INTERVALS,
        help='Kline intervals (default: all intervals)\n'
             'Example: -i 1m 1h 1d'
    )

    return parser


def create_trade_parser() -> argparse.ArgumentParser:
    """Create parser for trade downloads."""
    return create_base_parser(
        "Download individual trade data from Binance public data"
    )


def create_agg_trade_parser() -> argparse.ArgumentParser:
    """Create parser for aggregated trade downloads."""
    return create_base_parser(
        "Download aggregated trade data from Binance public data"
    )


def create_liquidation_snapshot_parser() -> argparse.ArgumentParser:
    """Create parser for liquidation snapshot downloads."""
    parser = create_base_parser(
        "Download liquidation snapshot data from Binance COIN-M futures"
    )

    # Liquidation snapshot is for cm futures, make -t optional
    for action in parser._actions:
        if action.dest == 'type':
            action.required = False
            action.default = 'cm'  # Default to COIN-M futures
            action.help = 'Market type (default: cm for this script)'

    return parser


def create_book_ticker_parser() -> argparse.ArgumentParser:
    """Create parser for book ticker downloads."""
    parser = create_base_parser(
        "Download book ticker (best bid/ask) data from Binance"
    )

    # Book ticker supports um and cm, make -t optional
    for action in parser._actions:
        if action.dest == 'type':
            action.required = False
            action.default = 'um'  # Default to USD-M futures
            action.help = 'Market type (default: um for this script)'

    return parser


def create_depth_parser() -> argparse.ArgumentParser:
    """Create parser for depth data downloads."""
    parser = create_base_parser(
        "Download order book depth data from Binance"
    )

    # Depth supports spot and um, make -t optional
    for action in parser._actions:
        if action.dest == 'type':
            action.required = False
            action.default = 'spot'  # Default to spot
            action.help = 'Market type (default: spot for this script)'

    return parser


def create_funding_rate_parser() -> argparse.ArgumentParser:
    """Create parser for funding rate downloads."""
    parser = create_base_parser(
        "Download funding rate history from Binance futures public data\n"
        "Note: Only daily data is downloaded by default (monthly data is skipped)"
    )

    # Funding rate is for um/cm futures, make -t optional and default to um
    for action in parser._actions:
        if action.dest == 'type':
            action.required = False
            action.default = 'um'  # Default to USD-M futures
            action.help = 'Market type (default: um for this script)'
        elif action.dest == 'skip_monthly':
            # Default to skipping monthly data for funding rate
            action.default = 1

    return parser


def create_option_parser() -> argparse.ArgumentParser:
    """Create parser for option downloads with pre-configured trading type."""
    parser = create_base_parser(
        "Download options data from Binance public data"
    )

    # Override -t and -s arguments to be optional for option downloads
    for action in parser._actions:
        if action.dest == 'type':
            action.required = False
            action.default = 'option'
            action.help = 'Market type (default: option for this script)'
        elif action.dest == 'symbols':
            action.required = False  # Make symbols optional

    return parser


def create_download_all_parser() -> argparse.ArgumentParser:
    """Create parser for multi-data-type downloads."""
    parser = create_base_parser(
        "Download multiple data types from Binance public data"
    )

    parser.add_argument(
        '-i', '--intervals',
        dest='intervals',
        default=VALID_INTERVALS,
        nargs='+',
        choices=VALID_INTERVALS,
        help='Kline intervals for kline data types (default: all intervals)'
    )

    parser.add_argument(
        '--data-types',
        dest='data_types',
        nargs='+',
        choices=VALID_DATA_TYPES,
        help='Data types to download (default: klines only)\n'
             'Example: --data-types klines trades aggTrades\n'
             'Use --all-data to download all supported data types'
    )

    parser.add_argument(
        '--all-data',
        dest='all_data',
        action='store_true',
        help='Download all data types supported by the market'
    )

    return parser


def parse_args(args: Optional[List[str]] = None, parser_type: str = 'klines') -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Arguments to parse (default: sys.argv[1:])
        parser_type: Type of parser to create

    Returns:
        Parsed arguments namespace
    """
    if args is None:
        args = sys.argv[1:]

    # Create appropriate parser
    if parser_type == 'download-all':
        parser = create_download_all_parser()
    elif parser_type == 'option':
        parser = create_option_parser()
    elif parser_type == 'fundingRate':
        parser = create_funding_rate_parser()
    elif parser_type == 'liquidationSnapshot':
        parser = create_liquidation_snapshot_parser()
    elif parser_type == 'bookTicker':
        parser = create_book_ticker_parser()
    elif parser_type == 'depth':
        parser = create_depth_parser()
    elif parser_type == 'aggTrades':
        parser = create_agg_trade_parser()
    elif parser_type == 'trades':
        parser = create_trade_parser()
    else:  # default to klines
        parser = create_kline_parser()

    return parser.parse_args(args)
