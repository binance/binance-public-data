"""
Base Downloader

This module provides the abstract base class for all data downloaders.
All specific downloaders inherit from BaseDownloader and implement
its abstract methods.
"""

import logging
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import List, Optional

from ..core.checksum_verifier import ChecksumVerifier
from ..core.data_type_config import DataType, get_data_type_spec
from ..core.retry_handler import RetryHandler
from ..utils.date_utils import (
    convert_to_date_object,
    get_default_end_date,
    get_default_start_date,
    is_date_in_range
)
from ..utils.file_operations import FileDownloader, get_all_symbols
from ..utils.path_builder import (
    get_data_path,
    get_file_save_path,
    get_checksum_filename
)
from ..utils.progress_tracker import ProgressTracker
from ..utils.symbol_dates import SymbolDateManager, get_symbol_date_manager, parse_date_filter

logger = logging.getLogger(__name__)


class BaseDownloader(ABC):
    """
    Abstract base class for all Binance data downloaders.

    Subclasses must implement the abstract methods to define
    the specific data type behavior.
    """

    def __init__(
        self,
        trading_type: str,
        file_downloader: Optional[FileDownloader] = None,
        retry_handler: Optional[RetryHandler] = None,
        checksum_verifier: Optional[ChecksumVerifier] = None,
        max_workers: int = 10,
        stop_on_continuous_failures: int = 50,
        symbol_date_manager: Optional[SymbolDateManager] = None,
        use_symbol_dates: bool = True
    ):
        """
        Initialize the downloader.

        Args:
            trading_type: Market type ('spot', 'um', or 'cm')
            file_downloader: Optional custom file downloader
            retry_handler: Optional custom retry handler
            checksum_verifier: Optional custom checksum verifier
            max_workers: Maximum number of threads for parallel downloads
            stop_on_continuous_failures: Stop download if N consecutive files fail (0 to disable)
            symbol_date_manager: Optional SymbolDateManager for start date lookup
            use_symbol_dates: Whether to use symbol date cache to avoid unnecessary requests
        """
        self.trading_type = trading_type
        self.file_downloader = file_downloader or FileDownloader()
        self.retry_handler = retry_handler or RetryHandler()
        self.checksum_verifier = checksum_verifier or ChecksumVerifier()
        self.max_workers = max_workers
        self.stop_on_continuous_failures = stop_on_continuous_failures
        self.consecutive_failures = 0
        self.symbol_date_manager = symbol_date_manager
        self.use_symbol_dates = use_symbol_dates

        # Get data type specification
        self.data_type = self.get_data_type()
        self.data_type_spec = get_data_type_spec(DataType(self.data_type))

        if not self.data_type_spec:
            raise ValueError(f"Unknown data type: {self.data_type}")

        # Validate market type support
        self._validate_market_type()

    def _validate_market_type(self):
        """Validate that the data type supports the specified market."""
        # Option is a special case - independent market
        if self.data_type == 'option':
            if self.trading_type not in ('option', 'spot', 'um', 'cm'):
                raise ValueError(f"Invalid trading_type for option data: {self.trading_type}. Use 'option'")
            return

        if self.trading_type == 'spot' and not self.data_type_spec.supports_spot:
            raise ValueError(f"{self.data_type} is not supported for spot market")
        if self.trading_type == 'um' and not self.data_type_spec.supports_um:
            raise ValueError(f"{self.data_type} is not supported for USD-M futures")
        if self.trading_type == 'cm' and not self.data_type_spec.supports_cm:
            raise ValueError(f"{self.data_type} is not supported for COIN-M futures")
        if self.trading_type == 'option' and self.data_type != 'option':
            raise ValueError(f"Only option data type supports 'option' trading_type")

    @abstractmethod
    def get_data_type(self) -> str:
        """
        Return the data type identifier.

        Returns:
            Data type string (e.g., 'klines', 'trades', 'aggTrades')
        """
        pass

    @abstractmethod
    def supports_intervals(self) -> bool:
        """
        Check if this data type supports interval parameter.

        Returns:
            True if intervals are supported, False otherwise
        """
        pass

    @abstractmethod
    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly data filename.

        Args:
            symbol: Trading symbol
            interval: Kline interval (None if not supported)
            year: Year as string
            month: Month (1-12)

        Returns:
            Formatted filename
        """
        pass

    @abstractmethod
    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily data filename.

        Args:
            symbol: Trading symbol
            interval: Kline interval (None if not supported)
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Formatted filename
        """
        pass

    def download_monthly(
        self,
        symbols: List[str],
        intervals: Optional[List[str]] = None,
        years: Optional[List[str]] = None,
        months: Optional[List[int]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        folder: Optional[str] = None,
        download_checksum: bool = False,
        verify_checksum: bool = False,
        skip_existing: bool = True,
        progress_tracker: Optional[ProgressTracker] = None
    ) -> int:
        """
        Download monthly data files.

        Args:
            symbols: List of trading symbols
            intervals: List of kline intervals (for data types that support intervals)
            years: List of years to download
            months: List of months to download
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            folder: Output folder
            download_checksum: Whether to download checksum files
            verify_checksum: Whether to verify checksums after download
            skip_existing: Whether to skip already downloaded files
            progress_tracker: Optional progress tracker

        Returns:
            Number of successfully downloaded files
        """
        if not self.data_type_spec.supports_monthly:
            logger.info(f"{self.data_type} does not have monthly files")
            return 0

        # Set defaults
        if not intervals:
            intervals = [None] if not self.supports_intervals() else []
        if not years:
            years = ['2020', '2021', '2022', '2023', '2024', '2025']
        if not months:
            months = list(range(1, 13))

        # Parse date filters
        start_date_obj = convert_to_date_object(start_date) if start_date else get_default_start_date()
        end_date_obj = convert_to_date_object(end_date) if end_date else get_default_end_date()

        # Display save location
        save_location = folder if folder else os.environ.get('STORE_DIRECTORY', os.getcwd())
        logger.info(f"Download location: {save_location}")

        downloaded_count = 0
        should_stop_early = False

        for symbol in symbols:
            logger.info(f"Downloading monthly {self.data_type} for {symbol}")
            consecutive_failures = 0  # Reset counter for each symbol
            max_consecutive_failures = 100  # Stop after 100 consecutive failures for one symbol

            # Get symbol's effective start date from cache if available
            symbol_effective_dates = {}
            if self.use_symbol_dates:
                intervals_to_check = intervals if intervals else [None]
                for interval in intervals_to_check:
                    cached_start = self._get_symbol_start_from_cache(symbol, interval)
                    if cached_start:
                        symbol_effective_dates[interval] = cached_start
                        logger.info(f"  Known start date for {symbol}" +
                                   (f" ({interval}): " if interval else ": ") +
                                   cached_start)

            # Prepare download tasks
            tasks = []
            intervals_to_process = intervals if intervals else [None]

            for interval in intervals_to_process:
                for year in years:
                    for month in months:
                        # Check date range
                        current_date = convert_to_date_object(f'{year}-{month:02d}-01')
                        if not is_date_in_range(f'{year}-{month:02d}-01', start_date_obj, end_date_obj):
                            continue

                        # Skip if before symbol's known start date
                        if interval in symbol_effective_dates:
                            if self._is_date_before_symbol_start(
                                f'{year}-{month:02d}-01',
                                symbol_effective_dates[interval]
                            ):
                                continue
                        elif None in symbol_effective_dates and interval is None:
                            if self._is_date_before_symbol_start(
                                f'{year}-{month:02d}-01',
                                symbol_effective_dates[None]
                            ):
                                continue

                        tasks.append((symbol, interval, year, month))

            # Download with thread pool
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for symbol, interval, year, month in tasks:
                    future = executor.submit(
                        self._download_monthly_file,
                        symbol, interval, year, month,
                        folder, download_checksum, verify_checksum, skip_existing
                    )
                    futures[future] = (symbol, year, month)

                for future in as_completed(futures):
                    if should_stop_early:
                        break

                    symbol, year, month = futures[future]
                    try:
                        result = future.result()
                        if result == "skipped":
                            # File already exists
                            consecutive_failures = 0
                        elif result:
                            # Download succeeded
                            downloaded_count += 1
                            consecutive_failures = 0
                        else:
                            # Download failed
                            consecutive_failures += 1
                            if consecutive_failures >= max_consecutive_failures:
                                logger.warning(f"Detected {consecutive_failures} consecutive download failures.")
                                logger.warning(f"Data may not be available for the requested date range.")
                                logger.warning(f"Please specify a more recent date range using -startDate and -endDate.")
                                logger.warning(f"Example: -startDate 2023-06-20 -endDate 2026-01-18")
                                logger.warning(f"Stopping download early to avoid excessive failures.")
                                should_stop_early = True
                                break

                        if progress_tracker:
                            is_skipped = (result == "skipped")
                            is_success = (result == True)
                            progress_tracker.update(symbol, is_success, skipped=is_skipped)

                    except Exception as e:
                        logger.error(f"Error downloading {symbol} for {year}-{month:02d}: {e}")
                        consecutive_failures += 1
                        if progress_tracker:
                            progress_tracker.update(symbol, False, skipped=False)

            if should_stop_early:
                break

        return downloaded_count

    def _download_monthly_file(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int,
        folder: Optional[str],
        download_checksum: bool,
        verify_checksum: bool,
        skip_existing: bool
    ) -> bool:
        """Download a single monthly file."""
        # Format filename
        filename = self.format_monthly_filename(symbol, interval, year, month)

        # Build paths
        data_path = get_data_path(
            self.trading_type,
            self.data_type_spec.path_segment,
            "monthly",
            symbol,
            interval
        )

        save_path = get_file_save_path(
            self.trading_type,
            self.data_type_spec.path_segment,
            "monthly",
            symbol,
            filename,
            folder,
            interval=interval
        )

        # Check if file exists
        if skip_existing and os.path.exists(save_path):
            logger.info(f"File already exists, skipping: {os.path.basename(save_path)}")
            return "skipped"

        # Build date string for logging
        date_str = f"{year}-{month:02d}"

        # Download data file
        success = self.file_downloader.download_file(
            data_path,
            filename,
            save_path,
            symbol=symbol,
            date_str=date_str
        )

        # Download and verify checksum
        if success and download_checksum:
            checksum_filename = get_checksum_filename(filename)
            checksum_save_path = save_path + ".CHECKSUM"
            self.file_downloader.download_file(data_path, checksum_filename, checksum_save_path)

            if verify_checksum:
                self.checksum_verifier.verify_checksum(save_path, checksum_save_path)

        return success

    def download_daily(
        self,
        symbols: List[str],
        intervals: Optional[List[str]] = None,
        dates: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        folder: Optional[str] = None,
        download_checksum: bool = False,
        verify_checksum: bool = False,
        skip_existing: bool = True,
        progress_tracker: Optional[ProgressTracker] = None
    ) -> int:
        """
        Download daily data files with multi-threading support.

        Args:
            symbols: List of trading symbols
            intervals: List of kline intervals (for data types that support intervals)
            dates: List of specific dates to download
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            folder: Output folder
            download_checksum: Whether to download checksum files
            verify_checksum: Whether to verify checksums after download
            skip_existing: Whether to skip already downloaded files
            progress_tracker: Optional progress tracker

        Returns:
            Number of successfully downloaded files
        """
        if not self.data_type_spec.supports_daily:
            logger.info(f"{self.data_type} does not have daily files")
            return 0

        # Parse date filters
        start_date_obj = convert_to_date_object(start_date) if start_date else get_default_start_date()
        end_date_obj = convert_to_date_object(end_date) if end_date else get_default_end_date()

        # Display save location
        save_location = folder if folder else os.environ.get('STORE_DIRECTORY', os.getcwd())
        logger.info(f"Download location: {save_location}")

        downloaded_count = 0
        should_stop_early = False

        for symbol in symbols:
            logger.info(f"Downloading daily {self.data_type} for {symbol}")
            consecutive_failures = 0  # Reset counter for each symbol
            max_consecutive_failures = 100  # Stop after 100 consecutive failures for one symbol

            # Get symbol's effective start date from cache if available
            symbol_effective_dates = {}
            if self.use_symbol_dates:
                intervals_to_check = intervals if intervals else [None]
                for interval in intervals_to_check:
                    cached_start = self._get_symbol_start_from_cache(symbol, interval)
                    if cached_start:
                        symbol_effective_dates[interval] = cached_start
                        logger.info(f"  Known start date for {symbol}" +
                                   (f" ({interval}): " if interval else ": ") +
                                   cached_start)

            # Prepare download tasks
            tasks = []
            intervals_to_process = intervals if intervals else [None]

            for interval in intervals_to_process:
                dates_to_process = dates if dates else self._generate_date_range(start_date_obj, end_date_obj)

                for date_str in dates_to_process:
                    # Check date range
                    if not is_date_in_range(date_str, start_date_obj, end_date_obj):
                        continue

                    # Skip if before symbol's known start date
                    if interval in symbol_effective_dates:
                        if self._is_date_before_symbol_start(
                            date_str,
                            symbol_effective_dates[interval]
                        ):
                            continue
                    elif None in symbol_effective_dates and interval is None:
                        if self._is_date_before_symbol_start(
                            date_str,
                            symbol_effective_dates[None]
                        ):
                            continue

                    tasks.append((symbol, interval, date_str))

            # Download with thread pool
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for symbol, interval, date_str in tasks:
                    future = executor.submit(
                        self._download_daily_file,
                        symbol, interval, date_str,
                        folder, download_checksum, verify_checksum, skip_existing
                    )
                    futures[future] = (symbol, date_str)

                for future in as_completed(futures):
                    if should_stop_early:
                        break

                    symbol, date_str = futures[future]
                    try:
                        result = future.result()
                        if result == "skipped":
                            # File already exists
                            consecutive_failures = 0
                        elif result:
                            # Download succeeded
                            downloaded_count += 1
                            consecutive_failures = 0
                        else:
                            # Download failed
                            consecutive_failures += 1
                            if consecutive_failures >= max_consecutive_failures:
                                logger.warning(f"Detected {consecutive_failures} consecutive download failures.")
                                logger.warning(f"Data may not be available for the requested date range.")
                                logger.warning(f"Please specify a more recent date range using -startDate and -endDate.")
                                logger.warning(f"Example: -startDate 2023-06-20 -endDate 2026-01-18")
                                logger.warning(f"Stopping download early to avoid excessive failures.")
                                should_stop_early = True
                                break

                        if progress_tracker:
                            is_skipped = (result == "skipped")
                            is_success = (result == True)
                            progress_tracker.update(symbol, is_success, skipped=is_skipped)

                    except Exception as e:
                        logger.error(f"Error downloading {symbol} for {date_str}: {e}")
                        consecutive_failures += 1
                        if progress_tracker:
                            progress_tracker.update(symbol, False, skipped=False)

            if should_stop_early:
                break

        return downloaded_count

    def _download_daily_file(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str,
        folder: Optional[str],
        download_checksum: bool,
        verify_checksum: bool,
        skip_existing: bool
    ) -> bool:
        """Download a single daily file."""
        # Format filename
        filename = self.format_daily_filename(symbol, interval, date_str)

        # Build paths
        data_path = get_data_path(
            self.trading_type,
            self.data_type_spec.path_segment,
            "daily",
            symbol,
            interval
        )

        save_path = get_file_save_path(
            self.trading_type,
            self.data_type_spec.path_segment,
            "daily",
            symbol,
            filename,
            folder,
            interval=interval
        )

        # Check if file exists
        if skip_existing and os.path.exists(save_path):
            logger.info(f"File already exists, skipping: {os.path.basename(save_path)}")
            return "skipped"

        # Download data file with symbol and date info
        success = self.file_downloader.download_file(
            data_path,
            filename,
            save_path,
            symbol=symbol,
            date_str=date_str
        )

        # Download and verify checksum
        if success and download_checksum:
            checksum_filename = get_checksum_filename(filename)
            checksum_save_path = save_path + ".CHECKSUM"
            self.file_downloader.download_file(data_path, checksum_filename, checksum_save_path)

            if verify_checksum:
                self.checksum_verifier.verify_checksum(save_path, checksum_save_path)

        return success

    def _generate_date_range(self, start_date: date, end_date: date) -> List[str]:
        """Generate a list of date strings between start and end dates."""
        from datetime import timedelta
        delta = end_date - start_date
        return [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(delta.days + 1)
        ]

    def get_local_date_range(
        self,
        symbol: str,
        folder: Optional[str],
        time_period: str = "daily"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the start and end dates of locally downloaded files for a symbol.

        Args:
            symbol: Trading symbol
            folder: Folder where data is stored
            time_period: 'daily' or 'monthly'

        Returns:
            Tuple of (start_date, end_date) as YYYY-MM-DD strings, or (None, None) if no local data found
        """
        from datetime import datetime
        from ..utils.path_builder import get_data_save_folder

        save_folder = get_data_save_folder(
            self.trading_type,
            self.data_type_spec.path_segment,
            time_period,
            symbol,
            folder
        )

        if not os.path.exists(save_folder):
            return None, None

        # Get all zip files in the folder
        files = [f for f in os.listdir(save_folder) if f.endswith('.zip') and not f.endswith('.CHECKSUM')]

        if not files:
            return None, None

        # Extract dates from filenames
        dates = []
        for filename in files:
            # Try to extract date from filename
            # Format: SYMBOL-dataType-YYYY-MM-DD.zip or SYMBOL-dataType-YYYY-MM.zip (monthly)
            import re
            # Match date patterns
            daily_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            monthly_match = re.search(r'(\d{4})-(\d{2})\.zip$', filename)

            if daily_match:
                dates.append(daily_match.group(1))
            elif monthly_match:
                # Convert monthly to first day of month
                year, month = monthly_match.groups()
                dates.append(f"{year}-{month}-01")

        if not dates:
            return None, None

        dates.sort()
        return dates[0], dates[-1]

    def get_missing_date_ranges(
        self,
        symbol: str,
        web_start_date: str,
        web_end_date: str,
        folder: Optional[str],
        time_period: str = "daily"
    ) -> List[Tuple[str, str]]:
        """
        Get missing date ranges by comparing local files with available web data.

        Args:
            symbol: Trading symbol
            web_start_date: Start date of available data on web (YYYY-MM-DD)
            web_end_date: End date of available data on web (YYYY-MM-DD)
            folder: Folder where data is stored
            time_period: 'daily' or 'monthly'

        Returns:
            List of (start_date, end_date) tuples representing missing date ranges
        """
        local_start, local_end = self.get_local_date_range(symbol, folder, time_period)

        if not local_start or not local_end:
            # No local data, return full web range
            return [(web_start_date, web_end_date)]

        # Convert to date objects for comparison
        from datetime import datetime
        web_start = datetime.strptime(web_start_date, "%Y-%m-%d").date()
        web_end = datetime.strptime(web_end_date, "%Y-%m-%d").date()
        local_start_date = datetime.strptime(local_start, "%Y-%m-%d").date()
        local_end_date = datetime.strptime(local_end, "%Y-%m-%d").date()

        missing_ranges = []

        # Check for missing data before local range
        if web_start < local_start_date:
            from datetime import timedelta
            missing_end = local_start_date - timedelta(days=1)
            missing_ranges.append((web_start.strftime("%Y-%m-%d"), missing_end.strftime("%Y-%m-%d")))
            logger.info(f"Found missing data before local range: {web_start.strftime('%Y-%m-%d')} to {missing_end.strftime('%Y-%m-%d')}")

        # Check for missing data after local range
        if web_end > local_end_date:
            from datetime import timedelta
            missing_start = local_end_date + timedelta(days=1)
            missing_ranges.append((missing_start.strftime("%Y-%m-%d"), web_end.strftime("%Y-%m-%d")))
            logger.info(f"Found missing data after local range: {missing_start.strftime('%Y-%m-%d')} to {web_end.strftime('%Y-%m-%d')}")

        if not missing_ranges:
            logger.info(f"Local data is up to date for {symbol}: {local_start} to {local_end}")

        return missing_ranges

    @staticmethod
    def fetch_symbols(market_type: str) -> List[str]:
        """
        Fetch all trading symbols from Binance API.

        Args:
            market_type: Market type ('spot', 'um', or 'cm')

        Returns:
            List of trading symbols
        """
        return get_all_symbols(market_type)

    def _get_symbol_start_from_cache(
        self,
        symbol: str,
        interval: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the known start date for a symbol from the cache.

        Args:
            symbol: Trading symbol
            interval: Kline interval (optional)

        Returns:
            Start date as YYYY-MM-DD string, or None if not found
        """
        if not self.use_symbol_dates:
            return None

        # Use provided manager or get default instance
        manager = self.symbol_date_manager
        if not manager:
            manager = get_symbol_date_manager()

        if not manager or not manager.is_cache_available():
            return None

        return manager.get_symbol_start_date(
            self.trading_type,
            self.data_type,
            symbol,
            interval
        )

    def _is_date_before_symbol_start(
        self,
        date_str: str,
        symbol_start: str
    ) -> bool:
        """
        Check if a date is before the symbol's start date.

        Args:
            date_str: Date to check (YYYY-MM-DD)
            symbol_start: Symbol's start date (YYYY-MM-DD)

        Returns:
            True if date_str is before symbol_start
        """
        try:
            return date_str < symbol_start
        except (ValueError, TypeError):
            return False

    def get_effective_date_range(
        self,
        symbol: str,
        interval: Optional[str] = None,
        requested_start: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Get the effective date range for downloading a symbol's data.

        Takes into account both the requested date range and the symbol's
        actual known start date from the cache.

        Args:
            symbol: Trading symbol
            interval: Kline interval (optional)
            requested_start: User-requested start date (YYYY-MM-DD)

        Returns:
            Tuple of (effective_start_date, end_date)
        """
        from datetime import datetime

        # Get symbol's start date from cache
        symbol_start = self._get_symbol_start_from_cache(symbol, interval)

        if symbol_start:
            # Use the later of requested start or symbol start
            if requested_start:
                effective_start = max(symbol_start, requested_start)
            else:
                effective_start = symbol_start
            logger.info(f"  Using cached start date for {symbol}: {effective_start}")
        else:
            effective_start = requested_start or get_default_start_date().strftime("%Y-%m-%d")

        end_date = get_default_end_date().strftime("%Y-%m-%d")

        return effective_start, end_date
