"""
File Operations

This module provides file I/O utilities for downloading and managing data files.
"""

import logging
import os
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional

import certifi

from ..core.retry_handler import RetryHandler
from .path_builder import get_download_url

logger = logging.getLogger(__name__)


class FileDownloader:
    """
    Handles file download operations with progress tracking and retry logic.
    """

    def __init__(
        self,
        retry_handler: Optional[RetryHandler] = None,
        show_progress: bool = True
    ):
        """
        Initialize the file downloader.

        Args:
            retry_handler: Optional custom retry handler
            show_progress: Whether to show download progress bar
        """
        self.retry_handler = retry_handler or RetryHandler()
        self.show_progress = show_progress
        # Don't create ssl_context here - create it per download for thread safety
        self._total_downloaded = 0
        self._total_skipped = 0
        self._total_failed = 0

    def download_file(
        self,
        base_path: str,
        file_name: str,
        save_path: str,
        show_full_path: bool = False,
        symbol: Optional[str] = None,
        date_str: Optional[str] = None
    ) -> bool:
        """
        Download a file from Binance data server.

        Args:
            base_path: Base path on server (relative to BASE_URL)
            file_name: Name of the file
            save_path: Local path to save the file
            show_full_path: Whether to show full path in progress
            symbol: Trading symbol (for logging)
            date_str: Date string (for logging)

        Returns:
            True if download succeeded, False otherwise
        """
        # Check if file already exists
        if os.path.exists(save_path):
            self._total_skipped += 1
            # Build detailed info message
            info_parts = []
            if symbol:
                info_parts.append(f"Symbol: {symbol}")
            if date_str:
                info_parts.append(f"Date: {date_str}")
            info_msg = " | ".join(info_parts) if info_parts else os.path.basename(save_path)
            logger.info(f"[SKIP] File exists locally: {info_msg}")
            return True

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Construct download URL
        download_path = f"{base_path}{file_name}"
        download_url = get_download_url(download_path)

        # Build detailed info message for logging
        info_parts = []
        if symbol:
            info_parts.append(f"Symbol: {symbol}")
        if date_str:
            info_parts.append(f"Date: {date_str}")
        info_msg = " | ".join(info_parts) if info_parts else os.path.basename(save_path)

        logger.info(f"[DOWNLOAD] {info_msg}")

        # Create SSL context per download for thread safety
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        # Download with retry
        dl_file = self.retry_handler.download_with_retry(download_url, ssl_context)
        if dl_file is None:
            self._total_failed += 1
            logger.warning(f"[FAILED] {info_msg}")
            return False

        # Get file size for progress tracking
        length = dl_file.getheader('content-length')
        if length:
            length = int(length)
            blocksize = max(4096, length // 100)
        else:
            blocksize = 4096

        # Write file to disk
        try:
            with open(save_path, 'wb') as out_file:
                dl_progress = 0

                while True:
                    buf = dl_file.read(blocksize)
                    if not buf:
                        break
                    dl_progress += len(buf)
                    out_file.write(buf)

                    if self.show_progress and length:
                        self._show_progress(dl_progress, length, file_name)

            size_str = self._format_size(dl_progress) if dl_progress else 'unknown'
            logger.info(f"[OK] Download completed: {info_msg} | Size: {size_str}")
            self._total_downloaded += 1
            return True

        except Exception as e:
            self._total_failed += 1
            logger.error(f"[ERROR] Failed to write file: {info_msg} | Error: {e}")
            # Clean up partial download
            if os.path.exists(save_path):
                os.remove(save_path)
            return False

    def _show_progress(self, progress: int, total: int, filename: str = ""):
        """Show simplified download progress."""
        percentage = int(100 * progress / total)
        # Only print occasionally to reduce clutter
        if percentage % 25 == 0 or percentage == 100:
            sys.stdout.write(f"\r  {filename} ... {percentage}%")
            sys.stdout.flush()
        if percentage == 100:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}TB"

    def download_and_verify(
        self,
        base_path: str,
        file_name: str,
        save_path: str,
        checksum_path: Optional[str] = None,
        verifier=None
    ) -> bool:
        """
        Download a file and optionally verify its checksum.

        Args:
            base_path: Base path on server
            file_name: Name of the file
            save_path: Local path to save the file
            checksum_path: Path to checksum file (optional)
            verifier: ChecksumVerifier instance (optional)

        Returns:
            True if download and verification succeeded, False otherwise
        """
        # Download the file
        if not self.download_file(base_path, file_name, save_path):
            return False

        # Verify checksum if provided
        if checksum_path and verifier:
            success, message = verifier.download_and_verify_checksum(
                save_path, checksum_path
            )
            if not success:
                logger.warning(f"Checksum verification failed: {message}")
                return False

        return True

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists locally."""
        return os.path.exists(file_path)

    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get the size of a local file.

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return None


def get_all_symbols(market_type: str) -> list[str]:
    """
    Fetch all trading symbols from Binance API for a given market type.

    Args:
        market_type: Market type ('spot', 'um', 'cm', or 'option')

    Returns:
        List of symbol strings
    """
    urls = {
        'um': "https://fapi.binance.com/fapi/v1/exchangeInfo",
        'cm': "https://dapi.binance.com/dapi/v1/exchangeInfo",
        'spot': "https://api.binance.com/api/v3/exchangeInfo",
        'option': "https://eapi.binance.com/eapi/v1/exchangeInfo"
    }

    if market_type not in urls:
        logger.error(f"Unsupported market type for symbol fetching: {market_type}")
        return []

    try:
        import json
        response = urllib.request.urlopen(urls[market_type], timeout=10).read()
        data = json.loads(response)

        # Option market now uses BVOLIndex data (Bitcoin and Ethereum Volatility Index)
        if market_type == 'option':
            # Return fixed BVOLIndex symbols
            return ['BTCBVOLUSDT', 'ETHBVOLUSDT']
        else:
            return [symbol['symbol'] for symbol in data['symbols']]
    except Exception as e:
        logger.error(f"Failed to fetch symbols for {market_type}: {e}")
        return []


# Default file downloader instance
default_downloader = FileDownloader()
