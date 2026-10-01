"""
Data Explorer

Auto-discovers available data types, symbols, and date ranges from Binance public data.
"""

import logging
import re
import urllib.request
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataExplorer:
    """
    Explores Binance public data structure to discover available data types,
    symbols, and date ranges.
    """

    def __init__(self, base_url: str = "https://data.binance.vision/"):
        """
        Initialize the data explorer.

        Args:
            base_url: Base URL for Binance public data
        """
        self.base_url = base_url

    def list_data_types(self, market: str = "um", time_period: str = "daily") -> List[str]:
        """
        List available data types for a given market.

        Args:
            market: Market type ('um' or 'cm')
            time_period: Time period ('daily' or 'monthly')

        Returns:
            List of data type names
        """
        # Known data types for futures markets
        if market in ['um', 'cm']:
            return [
                'klines',
                'trades',
                'aggTrades',
                'indexPriceKlines',
                'markPriceKlines',
                'premiumIndexKlines',
                'fundingRate',
                'bookTicker',
                'depth',
            ]
        elif market == 'spot':
            return ['klines', 'trades', 'aggTrades', 'depth']
        else:
            return []

    def discover_symbols_for_data_type(
        self,
        market: str,
        data_type: str,
        time_period: str = "daily"
    ) -> List[str]:
        """
        Discover available symbols for a specific data type.

        This uses the Binance API to get the list of active trading symbols.

        Args:
            market: Market type ('um', 'cm', or 'spot')
            data_type: Data type (e.g., 'klines', 'trades')
            time_period: Time period ('daily' or 'monthly')

        Returns:
            List of symbol names
        """
        import json

        urls = {
            'um': "https://fapi.binance.com/fapi/v1/exchangeInfo",
            'cm': "https://dapi.binance.com/dapi/v1/exchangeInfo",
            'spot': "https://api.binance.com/api/v3/exchangeInfo"
        }

        if market not in urls:
            logger.error(f"Unsupported market type: {market}")
            return []

        try:
            response = urllib.request.urlopen(urls[market], timeout=10).read()
            data = json.loads(response)

            # Extract symbols from exchange info
            symbols = [symbol['symbol'] for symbol in data['symbols']]
            logger.info(f"Found {len(symbols)} symbols for {market} market")
            return symbols

        except Exception as e:
            logger.error(f"Failed to fetch symbols for {market}: {e}")
            return []

    def discover_date_range_for_symbol(
        self,
        market: str,
        data_type: str,
        symbol: str,
        time_period: str = "daily"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Discover the available date range for a specific symbol.

        Uses binary search to find the start and end dates efficiently.

        Args:
            market: Market type ('um', 'cm', or 'spot')
            data_type: Data type (e.g., 'klines', 'trades')
            symbol: Trading symbol
            time_period: Time period ('daily' or 'monthly')

        Returns:
            Tuple of (start_date, end_date) as YYYY-MM-DD strings, or (None, None) if no data found
        """
        from datetime import datetime, timedelta
        import ssl
        import certifi

        # Determine data type specific formats
        if data_type in ['klines', 'indexPriceKlines', 'markPriceKlines', 'premiumIndexKlines']:
            # Check with common intervals
            intervals_to_check = ['1d', '1h', '1m']
        else:
            intervals_to_check = [None]

        dates_found = []

        for interval in intervals_to_check:
            # Try recent dates first (last 30 days)
            for days_ago in range(0, 30):
                check_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

                # Build file path based on data type
                if market == 'spot':
                    if interval and data_type in ['klines']:
                        file_path = f"data/spot/{time_period}/{data_type}/{symbol}/{interval}/{symbol}-{interval}-{check_date}.zip"
                    else:
                        file_path = f"data/spot/{time_period}/{data_type}/{symbol}/{symbol}-{data_type}-{check_date}.zip"
                elif market in ['um', 'cm']:
                    if interval and data_type in ['klines']:
                        file_path = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{interval}/{symbol}-{interval}-{check_date}.zip"
                    else:
                        file_path = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{symbol}-{data_type}-{check_date}.zip"
                else:
                    continue

                # Check if file exists
                url = f"{self.base_url}{file_path}"
                try:
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                    req = urllib.request.Request(url, method='HEAD')
                    response = urllib.request.urlopen(req, context=ssl_context, timeout=2)
                    if response.code == 200:
                        dates_found.append(check_date)
                        break  # Found a recent file, no need to check more
                except:
                    continue

            if dates_found:
                break  # Found data with this interval

        if not dates_found:
            # No recent data found, try checking with a wider range
            # Check a few key dates from different years
            test_dates = ['2024-12-01', '2024-06-01', '2024-01-01', '2023-06-01']

            for interval in intervals_to_check:
                for check_date in test_dates:
                    if market == 'spot':
                        if interval and data_type in ['klines']:
                            file_path = f"data/spot/{time_period}/{data_type}/{symbol}/{interval}/{symbol}-{interval}-{check_date}.zip"
                        else:
                            file_path = f"data/spot/{time_period}/{data_type}/{symbol}/{symbol}-{data_type}-{check_date}.zip"
                    elif market in ['um', 'cm']:
                        if interval and data_type in ['klines']:
                            file_path = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{interval}/{symbol}-{interval}-{check_date}.zip"
                        else:
                            file_path = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{symbol}-{data_type}-{check_date}.zip"
                    else:
                        continue

                    url = f"{self.base_url}{file_path}"
                    try:
                        ssl_context = ssl.create_default_context(cafile=certifi.where())
                        req = urllib.request.Request(url, method='HEAD')
                        response = urllib.request.urlopen(req, context=ssl_context, timeout=2)
                        if response.code == 200:
                            dates_found.append(check_date)
                            break
                    except:
                        continue

                if dates_found:
                    break

        if not dates_found:
            logger.debug(f"No data found for {market}/{data_type}/{symbol}")
            return None, None

        # If we found at least one date, use a heuristic to determine the range
        # For now, return the found date as both start and end
        # This can be improved later with binary search
        dates_found.sort()
        start_date = dates_found[0]
        end_date = datetime.now().strftime("%Y-%m-%d")

        logger.debug(f"Date range for {symbol}: {start_date} to {end_date} (estimated)")
        return start_date, end_date

    def get_data_date_range_from_web(
        self,
        market: str,
        data_type: str,
        symbol: str,
        time_period: str = "daily"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the exact start and end date for a symbol's data from the web.

        Uses a fast step-based approach to find boundaries.

        Args:
            market: Market type ('um', 'cm', or 'spot')
            data_type: Data type (e.g., 'fundingRate', 'klines')
            symbol: Trading symbol
            time_period: Time period ('daily' or 'monthly')

        Returns:
            Tuple of (start_date, end_date) as YYYY-MM-DD strings, or (None, None) if no data found
        """
        from datetime import datetime, timedelta
        import ssl
        import certifi

        # Determine interval for data types that support it
        if data_type in ['klines', 'indexPriceKlines', 'markPriceKlines', 'premiumIndexKlines']:
            interval = '1d'  # Use daily as default interval
        else:
            interval = None

        # Define reasonable default date ranges based on data type
        # Most Binance data started around 2020
        default_start_date = datetime(2020, 1, 1)
        latest_date = datetime.now()

        # Function to check if a file exists for a given date
        def check_date_exists(check_date: datetime) -> bool:
            date_str = check_date.strftime("%Y-%m-%d")

            # Build file path based on data type
            if market == 'spot':
                if interval and data_type in ['klines']:
                    file_path = f"data/spot/{time_period}/{data_type}/{symbol}/{interval}/{symbol}-{interval}-{date_str}.zip"
                else:
                    file_path = f"data/spot/{time_period}/{data_type}/{symbol}/{symbol}-{data_type}-{date_str}.zip"
            elif market in ['um', 'cm']:
                if interval and data_type in ['klines']:
                    file_path = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{interval}/{symbol}-{interval}-{date_str}.zip"
                else:
                    file_path = f"data/futures/{market}/{time_period}/{data_type}/{symbol}/{symbol}-{data_type}-{date_str}.zip"
            else:
                return False

            url = f"{self.base_url}{file_path}"
            try:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                req = urllib.request.Request(url, method='HEAD')
                response = urllib.request.urlopen(req, context=ssl_context, timeout=5)
                return response.code == 200
            except Exception as e:
                logger.debug(f"Check failed for {date_str}: {e}")
                return False

        # Step 1: First check if recent data exists (last 7 days)
        logger.debug(f"Checking for recent data for {symbol}...")
        end_date = None
        for days_ago in range(0, 7):
            check_date = latest_date - timedelta(days=days_ago)
            if check_date_exists(check_date):
                end_date = check_date
                break

        if not end_date:
            # No recent data found, try a few key dates
            logger.debug(f"No recent data, trying key dates for {symbol}...")
            key_dates = [
                latest_date,
                latest_date - timedelta(days=1),
                latest_date - timedelta(days=7),
                latest_date - timedelta(days=30),
            ]
            for check_date in key_dates:
                if check_date_exists(check_date):
                    end_date = check_date
                    break

        if not end_date:
            logger.warning(f"No data found for {market}/{data_type}/{symbol} - cannot determine end date")
            return None, None

        # Step 2: Find the start date by stepping back in large increments
        logger.debug(f"Finding start date for {symbol}...")
        start_date = None

        # First try to find the earliest date by stepping back
        # Use progressively smaller steps for efficiency
        current_date = end_date
        step_sizes = [90, 30, 7, 1]  # Days to step back

        for step_size in step_sizes:
            while True:
                test_date = current_date - timedelta(days=step_size)
                if test_date < default_start_date:
                    test_date = default_start_date

                if check_date_exists(test_date):
                    current_date = test_date
                    # If we're at the default start date, we found the boundary
                    if test_date == default_start_date:
                        break
                else:
                    # Data doesn't exist at this date, so current_date might be close to start
                    break

            if current_date == default_start_date:
                break

        # Now do a fine-grained search forward from current_date to find actual start
        # Move forward day by day until we find data
        search_start = current_date
        while search_start < end_date:
            if check_date_exists(search_start):
                start_date = search_start
                break
            search_start += timedelta(days=1)

        # If we didn't find start with fine search, use end_date as fallback
        if not start_date:
            start_date = end_date

        # Step 3: Fine-tune end date by checking forward from current end_date
        # (in case there are newer files)
        logger.debug(f"Fine-tuning end date for {symbol}...")
        test_date = end_date + timedelta(days=1)
        max_days_forward = 7  # Only check up to 7 days forward
        days_checked = 0
        while test_date <= latest_date and days_checked < max_days_forward:
            if check_date_exists(test_date):
                end_date = test_date
                test_date += timedelta(days=1)
                days_checked += 1
            else:
                break

        if start_date and end_date:
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            logger.info(f"Data range found for {symbol}: {start_str} to {end_str}")
            return start_str, end_str
        else:
            logger.warning(f"Could not determine date range for {market}/{data_type}/{symbol}")
            return None, None

    def explore_market(
        self,
        market: str = "um",
        data_types: Optional[List[str]] = None,
        time_period: str = "daily",
        max_symbols: Optional[int] = None
    ) -> Dict[str, Dict[str, Tuple[str, str]]]:
        """
        Explore a market and discover all available data.

        Args:
            market: Market type ('um', 'cm', or 'spot')
            data_types: List of data types to explore (None = all available)
            time_period: Time period ('daily' or 'monthly')
            max_symbols: Maximum number of symbols to explore per data type (None = all)

        Returns:
            Dictionary mapping data_type -> {symbol -> (start_date, end_date)}
        """
        # Get data types to explore
        if data_types is None:
            data_types = self.list_data_types(market, time_period)

        result = {}

        for data_type in data_types:
            logger.info(f"Exploring {market}/{data_type}")
            result[data_type] = {}

            # Get symbols for this data type
            symbols = self.discover_symbols_for_data_type(market, data_type, time_period)

            if max_symbols:
                symbols = symbols[:max_symbols]

            # Discover date range for each symbol
            for i, symbol in enumerate(symbols):
                if (i + 1) % 100 == 0:
                    logger.info(f"  Progress: {i + 1}/{len(symbols)} symbols explored")

                start_date, end_date = self.discover_date_range_for_symbol(
                    market, data_type, symbol, time_period
                )

                if start_date and end_date:
                    result[data_type][symbol] = (start_date, end_date)

            logger.info(f"  Found {len(result[data_type])} symbols with data for {data_type}")

        return result


def create_download_script_from_exploration(
    exploration_result: Dict[str, Dict[str, Tuple[str, str]]],
    market: str,
    output_folder: str
) -> str:
    """
    Create a shell script to download all discovered data.

    Args:
        exploration_result: Result from explore_market()
        market: Market type
        output_folder: Output folder path

    Returns:
        Shell script content
    """
    lines = [
        "#!/bin/bash",
        "#",
        f"# Auto-generated download script for {market.upper()} futures data",
        f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "#",
        "",
        "cd \"$(dirname \"$0\")\"",
        "",
    ]

    for data_type, symbols in exploration_result.items():
        lines.append(f"\n# Download {data_type}")
        lines.append(f"echo 'Downloading {data_type}...'")

        for symbol, (start_date, end_date) in symbols.items():
            lines.append(
                f"python scripts/download-{to_script_name(data_type)}.py "
                f"-t {market} "
                f"-s {symbol} "
                f"-startDate {start_date} "
                f"-endDate {end_date} "
                f"-folder {output_folder}"
            )

    lines.append("\necho 'All downloads completed!'")

    return "\n".join(lines)


def to_script_name(data_type: str) -> str:
    """Convert data type to script name."""
    # Convert camelCase to kebab-case
    import re
    return re.sub('([A-Z])', r'-\1', data_type).lower().lstrip('-')


def save_exploration_report(
    exploration_result: Dict[str, Dict[str, Tuple[str, str]]],
    market: str,
    output_file: str
):
    """
    Save exploration results to a file.

    Args:
        exploration_result: Result from explore_market()
        market: Market type
        output_file: Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {market.upper()} Market Data Exploration Report\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        total_symbols = sum(len(symbols) for symbols in exploration_result.values())
        f.write(f"Total Data Types: {len(exploration_result)}\n")
        f.write(f"Total Symbols with Data: {total_symbols}\n\n")

        for data_type, symbols in exploration_result.items():
            f.write(f"\n## {data_type}\n")
            f.write(f"Symbols: {len(symbols)}\n\n")

            for symbol, (start_date, end_date) in sorted(symbols.items()):
                f.write(f"  {symbol}: {start_date} to {end_date}\n")

    logger.info(f"Exploration report saved to {output_file}")
