"""
Retry Handler

This module provides retry mechanism for downloads with exponential backoff.
"""

import logging
import time
import urllib.request
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Handles download retries with exponential backoff strategy.

    HTTP 404 errors are not retried as they indicate the file doesn't exist.
    Other errors are retried up to max_retries times with exponential backoff.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        exponential_backoff: bool = True
    ):
        """
        Initialize the retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry (reduced for faster failure detection)
            exponential_backoff: Whether to use exponential backoff (doubling delay each retry)
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.exponential_backoff = exponential_backoff

    def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Optional[Any]:
        """
        Execute a function with retry logic.

        Args:
            func: The function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call, or None if all retries fail
        """
        last_exception = None
        delay = self.initial_delay

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except urllib.error.HTTPError as e:
                # Don't retry 404 errors - file doesn't exist
                if e.code == 404:
                    logger.debug(f"File not found (404), not retrying: {e.url}")
                    return None
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"HTTP error on attempt {attempt + 1}/{self.max_retries + 1}: {e}"
                    )
                    time.sleep(delay)
                    if self.exponential_backoff:
                        delay *= 2
                else:
                    logger.error(f"Max retries reached for HTTP error: {e}")
            except urllib.error.URLError as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"URL error on attempt {attempt + 1}/{self.max_retries + 1}: {e}"
                    )
                    time.sleep(delay)
                    if self.exponential_backoff:
                        delay *= 2
                else:
                    logger.error(f"Max retries reached for URL error: {e}")
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Unexpected error on attempt {attempt + 1}/{self.max_retries + 1}: {e}"
                    )
                    time.sleep(delay)
                    if self.exponential_backoff:
                        delay *= 2
                else:
                    logger.error(f"Max retries reached for unexpected error: {e}")

        logger.error(f"All retry attempts failed: {last_exception}")
        return None

    def download_with_retry(
        self,
        url: str,
        ssl_context: Any
    ) -> Optional[Any]:
        """
        Download a URL with retry logic.

        Args:
            url: The URL to download
            ssl_context: SSL context for secure connections

        Returns:
            The file-like object from urllib.request.urlopen, or None if failed
        """
        def _download():
            logger.debug(f"Downloading: {url}")
            return urllib.request.urlopen(url, context=ssl_context, timeout=30)

        return self.execute_with_retry(_download)


# Default retry handler instance
default_retry_handler = RetryHandler()
