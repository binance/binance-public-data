"""
Symbol Start Date Manager

This module provides utilities for managing symbol start date information
to avoid unnecessary download requests for non-existent data.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


# Default path for symbol dates cache
DEFAULT_SYMBOL_DATES_PATH = "data/symbol_dates.json"
# Default fallback start date
DEFAULT_START_DATE = "2020-01-01"


class SymbolDateManager:
    """
    Manages symbol start date information for efficient downloads.

    This class loads and caches symbol start date information from a JSON file,
    allowing downloaders to skip requests for non-existent data.
    """

    def __init__(self, cache_file: str = None):
        """
        Initialize the symbol date manager.

        Args:
            cache_file: Path to the symbol dates JSON cache file.
                       If None, uses DEFAULT_SYMBOL_DATES_PATH.
        """
        self.cache_file = cache_file or DEFAULT_SYMBOL_DATES_PATH
        self._cache: Dict = {}
        self._load_cache()

    def _load_cache(self):
        """Load symbol dates from cache file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.debug(f"Loaded symbol dates from {self.cache_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load symbol dates cache: {e}")
                self._cache = {}
        else:
            logger.debug(f"Symbol dates cache not found at {self.cache_file}")
            self._cache = {}

    def save_cache(self, path: str = None):
        """
        Save current cache to file.

        Args:
            path: Optional custom path to save to
        """
        save_path = path or self.cache_file
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved symbol dates cache to {save_path}")

    def get_symbol_start_date(
        self,
        market: str,
        data_type: str,
        symbol: str,
        interval: str = None
    ) -> Optional[str]:
        """
        Get the known start date for a symbol's data.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbol: Trading symbol
            interval: Kline interval (for data types that support intervals)

        Returns:
            Start date as YYYY-MM-DD string, or None if not found
        """
        if not self._cache:
            return None

        market_data = self._cache.get(market, {})
        if not market_data:
            return None

        data_type_data = market_data.get(data_type, {})
        if not data_type_data:
            return None

        symbol_data = data_type_data.get(symbol, {})
        if not symbol_data:
            return None

        # For data types with intervals
        if interval:
            return symbol_data.get(interval)

        # For data types without intervals, look for _default key
        return symbol_data.get('_default')

    def get_symbols_start_date_after(
        self,
        market: str,
        data_type: str,
        symbols: List[str],
        interval: str = None
    ) -> Dict[str, str]:
        """
        Get start dates for multiple symbols.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbols: List of trading symbols
            interval: Kline interval (optional)

        Returns:
            Dictionary mapping symbol -> start_date (only for symbols with known dates)
        """
        result = {}
        for symbol in symbols:
            start_date = self.get_symbol_start_date(market, data_type, symbol, interval)
            if start_date:
                result[symbol] = start_date
        return result

    def set_symbol_start_date(
        self,
        market: str,
        data_type: str,
        symbol: str,
        start_date: str,
        interval: str = None
    ):
        """
        Set or update the start date for a symbol's data.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbol: Trading symbol
            start_date: Start date as YYYY-MM-DD string
            interval: Kline interval (optional)
        """
        if market not in self._cache:
            self._cache[market] = {}
        if data_type not in self._cache[market]:
            self._cache[market][data_type] = {}
        if symbol not in self._cache[market][data_type]:
            self._cache[market][data_type][symbol] = {}

        key = interval if interval else '_default'
        self._cache[market][data_type][symbol][key] = start_date

    def get_all_symbols_for_market(
        self,
        market: str,
        data_type: str = None
    ) -> List[str]:
        """
        Get all known symbols for a market.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Optional data type filter

        Returns:
            List of symbol names
        """
        if not self._cache or market not in self._cache:
            return []

        if data_type:
            return list(self._cache[market].get(data_type, {}).keys())

        # Get all unique symbols across all data types
        symbols = set()
        for dt_data in self._cache[market].values():
            symbols.update(dt_data.keys())
        return list(symbols)

    def get_latest_date_for_symbol(
        self,
        market: str,
        data_type: str,
        symbol: str,
        interval: str = None
    ) -> Optional[str]:
        """
        Get the latest known date for a symbol's data.
        Returns the current date if symbol has any data.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbol: Trading symbol
            interval: Kline interval (optional)

        Returns:
            Latest date as YYYY-MM-DD string, or None if symbol not found
        """
        # Check if symbol has any data at all
        if self.get_symbol_start_date(market, data_type, symbol, interval):
            return datetime.now().strftime("%Y-%m-%d")
        return None

    def should_skip_date(
        self,
        market: str,
        data_type: str,
        symbol: str,
        check_date: str,
        interval: str = None
    ) -> bool:
        """
        Check if a date should be skipped because it's before the symbol's start date.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbol: Trading symbol
            check_date: Date to check as YYYY-MM-DD string
            interval: Kline interval (optional)

        Returns:
            True if the date is before the symbol's known start date
        """
        start_date = self.get_symbol_start_date(market, data_type, symbol, interval)
        if not start_date:
            return False

        try:
            return check_date < start_date
        except (ValueError, TypeError):
            return False

    def get_effective_start_date(
        self,
        market: str,
        data_type: str,
        symbol: str,
        interval: str = None,
        requested_start: str = None
    ) -> str:
        """
        Get the effective start date for downloading, taking into account
        both the requested start date and the symbol's actual start date.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbol: Trading symbol
            interval: Kline interval (optional)
            requested_start: User-requested start date (YYYY-MM-DD)

        Returns:
            Effective start date (later of requested or symbol start)
        """
        symbol_start = self.get_symbol_start_date(market, data_type, symbol, interval)
        if not symbol_start:
            return requested_start or DEFAULT_START_DATE

        if not requested_start:
            return symbol_start

        # Return the later date
        try:
            return max(symbol_start, requested_start)
        except (ValueError, TypeError):
            return requested_start

    def get_date_range_for_symbols(
        self,
        market: str,
        data_type: str,
        symbols: List[str],
        interval: str = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the overall date range covering multiple symbols.

        Args:
            market: Market type ('spot', 'um', 'cm')
            data_type: Data type (e.g., 'klines', 'trades')
            symbols: List of trading symbols
            interval: Kline interval (optional)

        Returns:
            Tuple of (earliest_start_date, latest_end_date) or (None, None)
        """
        dates = []
        for symbol in symbols:
            start = self.get_symbol_start_date(market, data_type, symbol, interval)
            if start:
                dates.append(start)

        if not dates:
            return None, None

        return min(dates), datetime.now().strftime("%Y-%m-%d")

    def get_metadata(self) -> Dict:
        """
        Get metadata from the cache.

        Returns:
            Metadata dictionary or empty dict
        """
        return self._cache.get('_metadata', {})

    def is_cache_available(self) -> bool:
        """
        Check if the cache has any useful data.

        Returns:
            True if cache has symbol data
        """
        if not self._cache:
            return False

        # Check if any market has data
        for key in self._cache.keys():
            if key != '_metadata' and isinstance(self._cache[key], dict):
                return True

        return False


def get_symbol_date_manager(cache_file: str = None) -> SymbolDateManager:
    """
    Get a singleton instance of the symbol date manager.

    Args:
        cache_file: Optional custom cache file path

    Returns:
        SymbolDateManager instance
    """
    return SymbolDateManager(cache_file)


def parse_date_filter(
    requested_start: str,
    symbol_start: str,
    default_start: str = DEFAULT_START_DATE
) -> str:
    """
    Determine the actual start date to use for downloading.

    Args:
        requested_start: User-requested start date (YYYY-MM-DD) or None
        symbol_start: Symbol's known start date (YYYY-MM-DD) or None
        default_start: Default start date if neither is specified

    Returns:
        Effective start date as YYYY-MM-DD string
    """
    if not requested_start and not symbol_start:
        return default_start

    if not requested_start:
        return symbol_start

    if not symbol_start:
        return requested_start

    # Use the later date
    try:
        return max(requested_start, symbol_start)
    except (ValueError, TypeError):
        return requested_start


def split_symbols_by_known_dates(
    symbols: List[str],
    known_dates: Dict[str, str],
    requested_start: str = None
) -> Tuple[List[str], Dict[str, str]]:
    """
    Split symbols into those with and without known start dates.

    Args:
        symbols: List of all symbols
        known_dates: Dictionary of symbol -> start_date
        requested_start: Optional requested start date to compare against

    Returns:
        Tuple of (symbols_with_unknown_dates, symbols_with_adjusted_dates)
    """
    unknown = []
    adjusted = {}

    for symbol in symbols:
        if symbol not in known_dates:
            unknown.append(symbol)
        elif requested_start and known_dates[symbol] > requested_start:
            adjusted[symbol] = known_dates[symbol]

    return unknown, adjusted
