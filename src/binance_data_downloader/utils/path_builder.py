"""
Path Builder

This module provides utilities for building URLs and file paths
for Binance public data downloads.
"""

import os
from typing import Optional


# Base URL for Binance public data
BASE_URL = "https://data.binance.vision/"


def get_download_url(file_path: str) -> str:
    """
    Construct the full download URL for a file.

    Args:
        file_path: Relative path from BASE_URL

    Returns:
        Full URL to download the file
    """
    return f"{BASE_URL}{file_path}"


def get_data_path(
    trading_type: str,
    data_type: str,
    time_period: str,
    symbol: str,
    interval: Optional[str] = None
) -> str:
    """
    Build the relative path for a data file.

    Args:
        trading_type: Market type ('spot', 'um', 'cm', or 'option')
        data_type: Type of data ('klines', 'trades', 'aggTrades', etc.)
        time_period: Time period ('monthly' or 'daily')
        symbol: Trading symbol (e.g., 'BTCUSDT')
        interval: Kline interval (e.g., '1h', '1d'), only for data types that support intervals

    Returns:
        Relative path from BASE_URL
    """
    # Build base path
    if trading_type == 'option':
        # BVOLIndex data path
        base_path = f"data/option/{time_period}/BVOLIndex"
    elif trading_type == 'spot':
        base_path = f"data/spot/{time_period}/{data_type}"
    else:
        # um and cm futures
        base_path = f"data/futures/{trading_type}/{time_period}/{data_type}"

    # Add symbol
    path = f"{base_path}/{symbol.upper()}"

    # Add interval if provided
    if interval is not None:
        path = f"{path}/{interval}"

    # Add trailing slash
    return f"{path}/"


def get_destination_dir(
    file_path: str,
    folder: Optional[str] = None
) -> str:
    """
    Get the local destination directory for a file download.

    Args:
        file_path: Relative path from download root (e.g., 'data/spot/daily/trades/')
        folder: Custom output folder (overrides STORE_DIRECTORY env var)

    Returns:
        Absolute local directory path
    """
    # Determine base storage directory
    store_directory = folder
    if not store_directory:
        store_directory = os.environ.get('STORE_DIRECTORY')

    if not store_directory:
        # Default to project root directory
        # Try to detect project root by looking for 'data/' directory
        current_dir = os.getcwd()
        current_dir = os.path.abspath(current_dir)

        # If we're in a subdirectory (like src/, python/, scripts/), go up to project root
        # Project root is the directory containing data/ or python/, or scripts/
        if os.path.exists(os.path.join(current_dir, 'data')):
            # Already at project root with data/ directory
            project_root = current_dir
        else:
            # Go up to find project root
            temp_dir = current_dir
            project_root = current_dir
            while temp_dir and not os.path.exists(os.path.join(temp_dir, 'data')):
                parent = os.path.dirname(temp_dir)
                if parent == temp_dir:  # Reached root without finding data/ directory
                    project_root = current_dir
                    break
                temp_dir = parent

        store_directory = project_root

    return os.path.join(store_directory, file_path)


def get_file_save_path(
    trading_type: str,
    data_type: str,
    time_period: str,
    symbol: str,
    filename: str,
    folder: Optional[str] = None,
    date_range: Optional[str] = None,
    interval: Optional[str] = None
) -> str:
    """
    Build the complete local save path for a file.

    Args:
        trading_type: Market type ('spot', 'um', 'cm', or 'option')
        data_type: Type of data ('klines', 'trades', 'aggTrades', etc.)
        time_period: Time period ('monthly' or 'daily')
        symbol: Trading symbol
        filename: Name of the file
        folder: Custom output folder (should be the 'data' directory path)
        date_range: Optional date range for subdirectory creation
        interval: Kline interval (optional)

    Returns:
        Absolute local file path
    """
    # Build the base directory path
    base_path = get_data_path(trading_type, data_type, time_period, symbol, interval)

    # Add custom folder if specified
    if folder:
        # Remove 'data/' prefix from base_path since folder is already the data directory
        if base_path.startswith('data/'):
            base_path = base_path[5:]  # Remove 'data/' prefix
        base_path = os.path.join(folder, base_path)

    # Add date range if specified
    if date_range:
        # Replace spaces with underscores for valid directory names
        date_range_dir = date_range.replace(" ", "_")
        base_path = os.path.join(base_path, date_range_dir)

    # Combine with filename
    full_path = os.path.join(base_path, filename)

    # Get destination directory
    # Only use get_destination_dir if folder is not specified
    if not folder:
        dest_dir = get_destination_dir(base_path)
    else:
        dest_dir = os.path.dirname(full_path)

    # Ensure directory exists
    os.makedirs(dest_dir, exist_ok=True)

    return full_path


def get_checksum_filename(data_filename: str) -> str:
    """
    Get the checksum filename for a data file.

    Args:
        data_filename: Name of the data file (e.g., 'BTCUSDT-trades-2023-01.zip')

    Returns:
        Checksum filename (e.g., 'BTCUSDT-trades-2023-01.zip.CHECKSUM')
    """
    return f"{data_filename}.CHECKSUM"


def get_data_save_folder(
    trading_type: str,
    data_type: str,
    time_period: str,
    symbol: str,
    folder: Optional[str] = None,
    interval: Optional[str] = None
) -> str:
    """
    Get the local save folder path for a data type and symbol.

    Args:
        trading_type: Market type ('spot', 'um', 'cm', or 'option')
        data_type: Type of data ('klines', 'trades', 'aggTrades', etc.)
        time_period: Time period ('monthly' or 'daily')
        symbol: Trading symbol
        folder: Custom output folder (should be the 'data' directory path)
        interval: Kline interval (optional)

    Returns:
        Absolute local folder path
    """
    # Build the base directory path
    base_path = get_data_path(trading_type, data_type, time_period, symbol, interval)

    # Add custom folder if specified
    if folder:
        # Remove 'data/' prefix from base_path since folder is already the data directory
        if base_path.startswith('data/'):
            base_path = base_path[5:]  # Remove 'data/' prefix
        base_path = os.path.join(folder, base_path)

    # Get destination directory
    if not folder:
        dest_dir = get_destination_dir(base_path)
    else:
        dest_dir = base_path

    return dest_dir


def format_monthly_filename(
    symbol: str,
    data_type: str,
    year: str,
    month: int,
    interval: Optional[str] = None
) -> str:
    """
    Format a monthly data filename.

    Args:
        symbol: Trading symbol
        data_type: Type of data
        year: Year as string
        month: Month (1-12)
        interval: Kline interval (for data types that support intervals)

    Returns:
        Formatted filename
    """
    symbol_upper = symbol.upper()
    month_str = f"{month:02d}"

    if interval:
        return f"{symbol_upper}-{interval}-{year}-{month_str}.zip"
    else:
        return f"{symbol_upper}-{data_type}-{year}-{month_str}.zip"


def format_daily_filename(
    symbol: str,
    data_type: str,
    date_str: str,
    interval: Optional[str] = None
) -> str:
    """
    Format a daily data filename.

    Args:
        symbol: Trading symbol
        data_type: Type of data
        date_str: Date string in YYYY-MM-DD format
        interval: Kline interval (for data types that support intervals)

    Returns:
        Formatted filename
    """
    symbol_upper = symbol.upper()

    if interval:
        return f"{symbol_upper}-{interval}-{date_str}.zip"
    else:
        return f"{symbol_upper}-{data_type}-{date_str}.zip"
