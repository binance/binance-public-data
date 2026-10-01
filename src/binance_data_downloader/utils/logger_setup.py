"""
Logger Setup

This module provides logging configuration for the downloader framework.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default log directory
DEFAULT_LOG_DIR = "logs"

# Default log file
DEFAULT_LOG_FILE = "download.log"


def setup_logger(
    name: str = "binance_data_downloader",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Path to log file (default: logs/download.log)
        log_format: Log message format
        console: Whether to add console handler

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set format
    if log_format is None:
        log_format = DEFAULT_LOG_FORMAT
    formatter = logging.Formatter(log_format)

    # Add console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler
    if log_file:
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_default_log_file() -> str:
    """Get the default log file path."""
    log_dir = os.environ.get('LOG_DIR', DEFAULT_LOG_DIR)
    return os.path.join(log_dir, DEFAULT_LOG_FILE)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get an existing logger or create a new one with defaults.

    Args:
        name: Logger name (defaults to 'binance_data_downloader')

    Returns:
        Logger instance
    """
    if name is None:
        name = "binance_data_downloader"

    logger = logging.getLogger(name)

    # If logger doesn't have handlers, set up with defaults
    if not logger.handlers:
        log_file = get_default_log_file()
        setup_logger(name, log_file=log_file)

    return logger


def set_log_level(level: int, name: Optional[str] = None):
    """
    Change the log level for a logger.

    Args:
        level: New logging level
        name: Logger name (defaults to 'binance_data_downloader')
    """
    logger = logging.getLogger(name if name else "binance_data_downloader")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def log_level_from_string(level_str: str) -> int:
    """
    Convert a log level string to logging constant.

    Args:
        level_str: Log level string (e.g., 'DEBUG', 'INFO', 'WARNING')

    Returns:
        Logging level constant
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return level_map.get(level_str.upper(), logging.INFO)


class LogContext:
    """
    Context manager for temporary log configuration changes.
    """

    def __init__(self, logger: logging.Logger, level: Optional[int] = None):
        """
        Initialize the log context.

        Args:
            logger: Logger to modify
            level: Temporary log level
        """
        self.logger = logger
        self.new_level = level
        self.old_level = None

    def __enter__(self):
        """Enter the context and apply changes."""
        if self.new_level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and restore previous state."""
        if self.old_level is not None:
            self.logger.setLevel(self.old_level)
        return False
