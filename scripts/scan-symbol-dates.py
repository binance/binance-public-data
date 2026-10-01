#!/usr/bin/env python3
"""
Binance Symbol Data Start Date Scanner

This script scans the Binance public data server (data.binance.vision)
to discover the actual start date for each symbol's data.

The discovered information is saved to a JSON file that can be used
by downloaders to avoid unnecessary requests for non-existent data.

Features:
- Scans all market types: spot, um (USD-M futures), cm (COIN-M futures)
- Scans all data types: klines, trades, aggTrades, etc.
- Saves results to JSON for reuse
- Uses S3 API for efficient directory listing

Examples:
    # Scan all markets and data types
    python3 scripts/scan-symbol-dates.py

    # Scan only spot market
    python3 scripts/scan-symbol-dates.py -t spot

    # Scan specific data types
    python3 scripts/scan-symbol-dates.py -d klines trades

    # Specify output file
    python3 scripts/scan-symbol-dates.py -o data/symbol_dates.json

    # Resume from existing file (incremental update)
    python3 scripts/scan-symbol-dates.py --resume -o data/symbol_dates.json
"""

import argparse
import json
import logging
import os
import re
import signal
import ssl
import threading
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# Global timeout flag
_timeout_event = threading.Event()
_global_start_time = None
_global_timeout_seconds = 120  # 2 minutes default


# S3 Bucket URL for Binance public data
S3_BUCKET_URL = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"

# Binance API endpoints
BINANCE_API = {
    'spot': 'https://api.binance.com/api/v3/exchangeInfo',
    'um': 'https://fapi.binance.com/fapi/v1/exchangeInfo',
    'cm': 'https://dapi.binance.com/dapi/v1/exchangeInfo'
}

# Data type configurations
DATA_TYPES = {
    'spot': ['klines', 'trades', 'aggTrades', 'depth'],
    'um': ['klines', 'trades', 'aggTrades', 'indexPriceKlines', 'markPriceKlines',
           'premiumIndexKlines', 'fundingRate', 'bookTicker', 'depth'],
    'cm': ['klines', 'trades', 'aggTrades', 'indexPriceKlines', 'markPriceKlines',
           'fundingRate', 'liquidationSnapshot', 'bookTicker']
}

# Intervals to check for klines data
KLINES_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']

# Default date to use if no earlier data found
DEFAULT_START_DATE = "2020-01-01"


def setup_logger(level: str = 'INFO') -> logging.Logger:
    """Setup logger."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def check_timeout() -> bool:
    """Check if global timeout has been reached."""
    if _timeout_event.is_set():
        return True
    if _global_start_time is not None:
        elapsed = (datetime.now() - _global_start_time).total_seconds()
        if elapsed >= _global_timeout_seconds:
            _timeout_event.set()
            return True
    return False


def fetch_exchange_info(market: str, logger: logging.Logger = None, timeout: int = 30) -> Optional[Dict]:
    """
    Fetch exchange info from Binance API.
    
    Args:
        market: Market type ('spot', 'um', 'cm')
        logger: Logger instance
        timeout: Request timeout in seconds
    
    Returns:
        API response as dict or None if failed
    """
    url = BINANCE_API.get(market)
    if not url:
        if logger:
            logger.error(f"Unknown market type: {market}")
        return None
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response = urllib.request.urlopen(req, context=ssl_context, timeout=timeout)
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        if logger:
            logger.error(f"Failed to fetch exchange info for {market}: {e}")
        return None


def parse_exchange_info(market: str, data: Dict, logger: logging.Logger = None) -> Dict[str, Dict]:
    """
    Parse exchange info response to extract symbol start dates.
    
    Args:
        market: Market type ('spot', 'um', 'cm')
        data: API response data
        logger: Logger instance
    
    Returns:
        Dictionary mapping symbol -> {data_type -> start_date}
    """
    result = {}
    symbols = data.get('symbols', [])
    
    for symbol_info in symbols:
        symbol = symbol_info.get('symbol', '')
        if not symbol:
            continue
        
        # Try to get launch/listing time
        launch_time = None
        
        # Check various fields that might contain launch date
        if 'onboardDate' in symbol_info:
            launch_time = symbol_info['onboardDate']
        elif 'listingDate' in symbol_info:
            launch_time = symbol_info['listingDate']
        elif 'launchTime' in symbol_info:
            launch_time = symbol_info['launchTime']
        
        # Convert timestamp to date string
        if launch_time:
            try:
                if isinstance(launch_time, (int, float)):
                    # Unix timestamp in milliseconds
                    dt = datetime.fromtimestamp(launch_time / 1000)
                    start_date = dt.strftime('%Y-%m-%d')
                else:
                    start_date = str(launch_time)
            except:
                start_date = DEFAULT_START_DATE
        else:
            start_date = DEFAULT_START_DATE
        
        result[symbol] = {'_default': start_date}
    
    if logger:
        logger.info(f"Parsed {len(result)} symbols from {market} API")
    
    return result


def scan_market_via_api(
    market: str,
    logger: logging.Logger = None
) -> Dict[str, Dict[str, Dict]]:
    """
    Scan a market using Binance API.
    
    Args:
        market: Market type ('spot', 'um', 'cm')
        logger: Logger instance
    
    Returns:
        Dictionary with all data types containing symbol start dates
    """
    if logger:
        logger.info(f"Fetching {market} exchange info via API...")
    
    data = fetch_exchange_info(market, logger)
    if not data:
        return {}
    
    symbols_data = parse_exchange_info(market, data, logger)
    
    # Create result with all data types pointing to same symbol dates
    result = {}
    data_types = DATA_TYPES.get(market, [])
    
    for data_type in data_types:
        result[data_type] = symbols_data.copy()
    
    return result


def scan_all_markets_via_api(
    markets: List[str] = None,
    logger: logging.Logger = None
) -> Dict:
    """
    Scan all markets using Binance API (fast method).
    
    Args:
        markets: List of markets to scan ('spot', 'um', 'cm')
        logger: Logger instance
    
    Returns:
        Dictionary with all scanned data
    """
    if markets is None:
        markets = ['spot', 'um', 'cm']
    
    result = {}
    
    for market in markets:
        if check_timeout():
            if logger:
                logger.warning("Timeout reached, stopping API scan...")
            break
        
        market_data = scan_market_via_api(market, logger)
        if market_data:
            result[market] = market_data
    
    return result


def fetch_s3_xml(prefix: str, marker: str = None, timeout: int = 10, delimiter: str = None) -> Optional[str]:
    """
    Fetch S3 bucket listing XML for a given prefix.

    Args:
        prefix: S3 key prefix (e.g., 'data/spot/monthly/klines/')
        marker: Pagination marker for getting next page
        timeout: Request timeout in seconds
        delimiter: Delimiter for grouping (use '/' to get directories)

    Returns:
        XML content or None if failed
    """
    if check_timeout():
        return None
        
    url = f"{S3_BUCKET_URL}?prefix={prefix}"
    if delimiter:
        url += f"&delimiter={delimiter}"
    if marker:
        url += f"&marker={marker}"
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response = urllib.request.urlopen(req, context=ssl_context, timeout=timeout)
        return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None


def list_common_prefixes(prefix: str, logger: logging.Logger = None, max_pages: int = 20) -> List[str]:
    """
    List S3 common prefixes (subdirectories) for a given prefix.

    Uses delimiter='/' to efficiently get directory names.
    Supports pagination to get all results.

    Args:
        prefix: S3 key prefix
        logger: Logger instance
        max_pages: Maximum number of pages to fetch (safety limit)

    Returns:
        List of prefix names (without the full path)
    """
    prefixes = set()
    marker = None
    page_count = 0

    try:
        while page_count < max_pages:
            if check_timeout():
                break
            # Use delimiter='/' to get CommonPrefixes directly (much faster)
            xml_content = fetch_s3_xml(prefix, marker, delimiter='/')
            if not xml_content:
                break

            root = ET.fromstring(xml_content)
            namespaces = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}

            # Get CommonPrefixes (subdirectories)
            for common_prefix in root.findall('s3:CommonPrefixes', namespaces):
                prefix_elem = common_prefix.find('s3:Prefix', namespaces)
                if prefix_elem is not None:
                    full_prefix = prefix_elem.text
                    if full_prefix and full_prefix.startswith(prefix):
                        parts = full_prefix.rstrip('/').split('/')
                        if parts:
                            prefixes.add(parts[-1])

            # Check if there are more results
            is_truncated = root.find('s3:IsTruncated', namespaces)
            if is_truncated is not None and is_truncated.text == 'true':
                next_marker = root.find('s3:NextMarker', namespaces)
                if next_marker is not None and next_marker.text:
                    marker = next_marker.text
                    page_count += 1
                else:
                    # For CommonPrefixes, use last prefix as marker
                    common_prefixes = root.findall('s3:CommonPrefixes', namespaces)
                    if common_prefixes:
                        last_prefix = common_prefixes[-1].find('s3:Prefix', namespaces)
                        if last_prefix is not None and last_prefix.text:
                            marker = last_prefix.text
                            page_count += 1
                        else:
                            break
                    else:
                        break
            else:
                break

    except Exception as e:
        if logger:
            logger.debug(f"Error parsing XML for {prefix}: {e}")

    return sorted(prefixes)


def list_files_with_dates(prefix: str, logger: logging.Logger = None) -> List[Tuple[str, str]]:
    """
    List files with their dates from S3.

    Args:
        prefix: S3 key prefix
        logger: Logger instance

    Returns:
        List of (filename, date_str) tuples
    """
    xml_content = fetch_s3_xml(prefix)
    if not xml_content:
        return []

    files = []
    try:
        root = ET.fromstring(xml_content)
        namespaces = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}

        for content in root.findall('s3:Contents', namespaces):
            key_elem = content.find('s3:Key', namespaces)
            if key_elem is not None:
                key = key_elem.text
                # Skip checksum files
                if key and not key.endswith('.CHECKSUM'):
                    # Extract date from filename
                    # Patterns: SYMBOL-INTERVAL-YYYY-MM-DD.zip or SYMBOL-INTERVAL-YYYY-MM.zip
                    date_match = re.search(r'(\d{4}-\d{2}(?:-\d{2})?)\.zip$', key)
                    if date_match:
                        files.append((key, date_match.group(1)))

    except Exception as e:
        if logger:
            logger.debug(f"Error parsing XML for {prefix}: {e}")

    return sorted(files, key=lambda x: x[1])


def list_symbols_for_market_data_type(
    market: str,
    data_type: str,
    logger: logging.Logger = None
) -> List[str]:
    """
    List all symbols available for a market and data type.

    Uses daily data only for speed (most symbols are in daily).

    Args:
        market: Market type ('spot', 'um', 'cm')
        data_type: Data type (e.g., 'klines', 'trades')
        logger: Logger instance

    Returns:
        List of symbol names
    """
    all_symbols = set()

    # Use daily only for speed (it has most symbols)
    if market == 'spot':
        prefix = f"data/spot/daily/{data_type}/"
    else:
        prefix = f"data/futures/{market}/daily/{data_type}/"

    prefixes = list_common_prefixes(prefix, logger)

    # Filter for symbol names (exclude intervals like 1m, 1h, 1d)
    interval_pattern = r'^(\d+[mhdw]|1M)$'
    symbols = [p for p in prefixes if not re.match(interval_pattern, p)]
    all_symbols.update(symbols)

    if logger:
        logger.debug(f"Found {len(symbols)} symbols")

    return sorted(all_symbols)


def list_intervals_for_symbol(
    market: str,
    data_type: str,
    symbol: str,
    logger: logging.Logger = None
) -> List[str]:
    """
    List available intervals for a symbol (for klines data).

    Args:
        market: Market type ('spot', 'um', 'cm')
        data_type: Data type
        symbol: Trading symbol
        logger: Logger instance

    Returns:
        List of interval names
    """
    if market == 'spot':
        prefix = f"data/spot/monthly/{data_type}/{symbol}/"
    else:
        prefix = f"data/futures/{market}/monthly/{data_type}/{symbol}/"

    prefixes = list_common_prefixes(prefix, logger)

    # Filter for interval names
    interval_pattern = r'^(\d+[mhdw]|1M)$'
    intervals = [p for p in prefixes if re.match(interval_pattern, p)]

    return sorted(intervals)


def find_earliest_date_for_symbol_interval(
    market: str,
    data_type: str,
    symbol: str,
    interval: str = None,
    logger: logging.Logger = None
) -> Optional[str]:
    """
    Find the earliest available date for a symbol/interval.

    Checks both daily and monthly data to find the earliest date.

    Args:
        market: Market type ('spot', 'um', 'cm')
        data_type: Data type (e.g., 'klines', 'trades')
        symbol: Trading symbol
        interval: Interval for klines data
        logger: Logger instance

    Returns:
        Earliest date string (YYYY-MM-DD) or None
    """
    earliest_date = None

    # Check both daily and monthly
    for time_period in ['daily', 'monthly']:
        if interval:
            if market == 'spot':
                prefix = f"data/spot/{time_period}/{data_type}/{symbol}/{interval}/"
            else:
                prefix = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{interval}/"
        else:
            if market == 'spot':
                prefix = f"data/spot/{time_period}/{data_type}/{symbol}/"
            else:
                prefix = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/"

        files = list_files_with_dates(prefix, logger)

        if files:
            date_str = files[0][1]  # Earliest date
            if earliest_date is None or date_str < earliest_date:
                earliest_date = date_str

    return earliest_date


def _scan_symbol_task(
    market: str,
    data_type: str,
    symbol: str,
    supports_intervals: bool,
    check_intervals: bool,
    existing_data: Dict,
    logger: logging.Logger
) -> Tuple[str, Dict]:
    """
    Task to scan a single symbol (for parallel execution).
    """
    if check_timeout():
        return (symbol, {})
        
    symbol_data = {}

    if supports_intervals and check_intervals:
        # Get available intervals from S3
        intervals = list_intervals_for_symbol(market, data_type, symbol, logger)

        if not intervals:
            # Try default intervals - reduced for speed
            intervals = ['1d']

        for interval in intervals:
            if check_timeout():
                break
            # Check if we already have this data
            if existing_data and symbol in existing_data:
                if interval in existing_data[symbol]:
                    symbol_data[interval] = existing_data[symbol][interval]
                    continue

            start_date = find_earliest_date_for_symbol_interval(
                market, data_type, symbol, interval, logger
            )
            if start_date:
                symbol_data[interval] = start_date
    else:
        # No intervals
        if existing_data and symbol in existing_data:
            return (symbol, existing_data[symbol])

        start_date = find_earliest_date_for_symbol_interval(
            market, data_type, symbol, None, logger
        )
        if start_date:
            symbol_data['_default'] = start_date

    return (symbol, symbol_data)


def scan_market_data_type(
    market: str,
    data_type: str,
    existing_data: Dict = None,
    logger: logging.Logger = None,
    check_intervals: bool = True,
    max_workers: int = 20,
    max_symbols: int = 0
) -> Dict[str, Dict]:
    """
    Scan all symbols for a market and data type.

    Args:
        market: Market type ('spot', 'um', 'cm')
        data_type: Data type
        existing_data: Previously scanned data to resume from
        logger: Logger instance
        check_intervals: Whether to check intervals for klines
        max_workers: Number of parallel workers
        max_symbols: Maximum symbols to scan (0 = unlimited)

    Returns:
        Dictionary mapping symbol -> {interval -> start_date}
    """
    if check_timeout():
        if logger:
            logger.warning(f"Timeout reached, skipping {market}/{data_type}")
        return {}
        
    if logger:
        logger.info(f"Scanning {market}/{data_type}...")

    result = {}

    # Check if data type supports intervals
    supports_intervals = data_type in ['klines', 'indexPriceKlines', 'markPriceKlines', 'premiumIndexKlines']

    # Get list of symbols from S3
    symbols = list_symbols_for_market_data_type(market, data_type, logger)

    if not symbols:
        if logger:
            logger.warning(f"No symbols found for {market}/{data_type}")
        return result

    # Limit symbols if max_symbols is set
    if max_symbols > 0 and len(symbols) > max_symbols:
        symbols = symbols[:max_symbols]
        if logger:
            logger.info(f"Limited to {max_symbols} symbols (total available: more)")

    if logger:
        logger.info(f"Found {len(symbols)} symbols for {market}/{data_type}")

    # Parallel scanning of symbols
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _scan_symbol_task,
                market, data_type, symbol, supports_intervals,
                check_intervals, existing_data, logger
            ): symbol
            for symbol in symbols
        }
        
        completed = 0
        for future in as_completed(futures):
            if check_timeout():
                if logger:
                    logger.warning(f"Timeout reached during {market}/{data_type}, stopping...")
                break
                
            try:
                symbol, symbol_data = future.result(timeout=5)
                if symbol_data:
                    result[symbol] = symbol_data
            except Exception as e:
                pass
                
            completed += 1
            if logger and completed % 100 == 0:
                logger.info(f"  Progress: {completed}/{len(symbols)} symbols")

    if logger:
        logger.info(f"  Completed: {len(result)} symbols with data for {market}/{data_type}")

    return result


def scan_all_markets(
    markets: List[str] = None,
    data_types: Dict[str, List[str]] = None,
    existing_data: Dict = None,
    logger: logging.Logger = None,
    max_workers: int = 20,
    check_intervals: bool = True,
    max_symbols: int = 0
) -> Dict:
    """
    Scan all markets and data types.

    Args:
        markets: List of markets to scan ('spot', 'um', 'cm')
        data_types: Data types to scan for each market
        existing_data: Previously scanned data
        logger: Logger instance
        max_workers: Number of parallel workers
        check_intervals: Whether to check intervals
        max_symbols: Maximum symbols per data type (0 = unlimited)

    Returns:
        Dictionary with all scanned data
    """
    if markets is None:
        markets = ['spot', 'um', 'cm']

    if data_types is None:
        data_types = DATA_TYPES

    result = {}
    if existing_data:
        result = existing_data.copy()

    scan_tasks = []

    for market in markets:
        for data_type in data_types.get(market, []):
            scan_tasks.append((market, data_type))

    if logger:
        logger.info(f"Starting scan of {len(scan_tasks)} market/data type combinations...")

    # Sequential market/data_type scanning, parallel symbol scanning
    for market, data_type in scan_tasks:
        if check_timeout():
            if logger:
                logger.warning("Global timeout reached, stopping scan...")
            break
            
        if market not in result:
            result[market] = {}
        if data_type not in result[market]:
            result[market][data_type] = {}

        existing_market_data = None
        if existing_data and market in existing_data and data_type in existing_data[market]:
            existing_market_data = existing_data[market][data_type]

        scanned_data = scan_market_data_type(
            market, data_type, existing_market_data, logger, check_intervals, max_workers, max_symbols
        )
        result[market][data_type] = scanned_data

    return result


def save_scanned_data(data: Dict, output_file: str, logger: logging.Logger = None):
    """
    Save scanned data to JSON file.

    Args:
        data: Scanned data dictionary
        output_file: Output file path
        logger: Logger instance
    """
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if logger:
        logger.info(f"Data saved to {output_file}")


def load_scanned_data(input_file: str, logger: logging.Logger = None) -> Dict:
    """
    Load previously scanned data from JSON file.

    Args:
        input_file: Input file path
        logger: Logger instance

    Returns:
        Scanned data dictionary
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if logger:
            logger.info(f"Loaded existing data from {input_file}")
        return data
    except FileNotFoundError:
        if logger:
            logger.info(f"No existing data file found at {input_file}, starting fresh")
        return {}
    except json.JSONDecodeError as e:
        if logger:
            logger.warning(f"Error parsing existing data file: {e}")
        return {}


def print_summary(data: Dict, logger: logging.Logger = None):
    """
    Print summary of scanned data.

    Args:
        data: Scanned data dictionary
        logger: Logger instance
    """
    if logger:
        logger.info("=" * 70)
        logger.info("Scan Summary")
        logger.info("=" * 70)

    for market, market_data in data.items():
        if market == '_metadata':
            continue

        total_symbols = 0
        for data_type, symbols in market_data.items():
            if isinstance(symbols, dict):
                total_symbols += len(symbols)

        if logger:
            logger.info(f"{market.upper()}: {len(market_data)} data types, {total_symbols} total symbols")

        for data_type, symbols in market_data.items():
            if isinstance(symbols, dict):
                if logger:
                    logger.info(f"  - {data_type}: {len(symbols)} symbols")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Binance Symbol Data Start Date Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-t', '--market-type',
        type=str,
        nargs='+',
        choices=['spot', 'um', 'cm'],
        default=['spot', 'um', 'cm'],
        help='Market types to scan (default: all)'
    )

    parser.add_argument(
        '-d', '--data-types',
        type=str,
        nargs='+',
        help='Data types to scan (default: all available for market)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/symbol_dates.json',
        help='Output JSON file path (default: data/symbol_dates.json)'
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from existing output file (incremental update)'
    )

    parser.add_argument(
        '--no-intervals',
        action='store_true',
        help='Skip interval checking (faster, less detailed)'
    )

    parser.add_argument(
        '-log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=120,
        help='Global timeout in seconds (default: 120 = 2 minutes)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=20,
        help='Number of parallel workers (default: 20)'
    )

    parser.add_argument(
        '--max-symbols',
        type=int,
        default=0,
        help='Maximum symbols to scan per data type (0 = unlimited)'
    )

    parser.add_argument(
        '--api',
        action='store_true',
        help='Use Binance REST API instead of S3 scanning (much faster, recommended)'
    )

    args = parser.parse_args()

    # Setup global timeout
    global _global_timeout_seconds, _global_start_time
    _global_timeout_seconds = args.timeout
    _global_start_time = datetime.now()
    _timeout_event.clear()

    # Setup logging
    logger = setup_logger(args.log_level)

    logger.info("=" * 70)
    logger.info("Binance Symbol Data Start Date Scanner")
    logger.info("=" * 70)
    logger.info(f"Markets to scan: {', '.join(args.market_type)}")
    logger.info(f"Output file: {args.output}")
    logger.info(f"Resume mode: {args.resume}")
    logger.info(f"Check intervals: {not args.no_intervals}")
    logger.info(f"Timeout: {args.timeout} seconds")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Use API: {args.api}")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load existing data if resuming
    existing_data = {}
    if args.resume:
        existing_data = load_scanned_data(args.output, logger)

    # Filter data types if specified
    data_types_to_scan = DATA_TYPES.copy()
    if args.data_types:
        for market in args.market_type:
            if market in data_types_to_scan:
                data_types_to_scan[market] = [
                    dt for dt in args.data_types if dt in data_types_to_scan[market]
                ]

    # Start scanning
    start_time = datetime.now()

    if args.api:
        # Use fast API method
        scanned_data = scan_all_markets_via_api(
            markets=args.market_type,
            logger=logger
        )
        # Merge with existing data if resuming
        if existing_data:
            for market in existing_data:
                if market not in scanned_data:
                    scanned_data[market] = existing_data[market]
    else:
        # Use S3 scanning method
        scanned_data = scan_all_markets(
            markets=args.market_type,
            data_types=data_types_to_scan,
            existing_data=existing_data,
            logger=logger,
            max_workers=args.workers,
            check_intervals=not args.no_intervals,
            max_symbols=args.max_symbols
        )

    # Check if we timed out
    timed_out = check_timeout()

    # Add metadata
    scanned_data['_metadata'] = {
        'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'markets_scanned': args.market_type,
        'total_symbols': sum(
            len(symbols)
            for market in scanned_data
            if market != '_metadata'
            for data_type in scanned_data[market]
            for symbols in [scanned_data[market][data_type]]
            if isinstance(symbols, dict)
        )
    }

    # Save results
    save_scanned_data(scanned_data, args.output, logger)

    # Print summary
    print_summary(scanned_data, logger)

    elapsed_time = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 70)
    if timed_out:
        logger.warning(f"Scan TIMED OUT after {elapsed_time:.1f} seconds (partial results saved)")
    else:
        logger.info(f"Scan completed in {elapsed_time:.1f} seconds!")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
