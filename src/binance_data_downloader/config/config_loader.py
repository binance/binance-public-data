"""
Configuration Loader

This module provides configuration file loading and validation.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DownloadConfig:
    """Download configuration settings."""
    market_type: str = "spot"
    max_workers: int = 10
    output_directory: Optional[str] = None
    download_checksum: bool = False
    verify_checksum: bool = False
    skip_monthly: bool = False
    skip_daily: bool = False


@dataclass
class RetryConfig:
    """Retry configuration settings."""
    max_retries: int = 3
    initial_delay: float = 5.0
    exponential_backoff: bool = True


@dataclass
class DateRangeConfig:
    """Date range configuration settings."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    years: List[str] = field(default_factory=lambda: ['2020', '2021', '2022', '2023', '2024', '2025'])
    months: List[int] = field(default_factory=lambda: list(range(1, 13)))


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ProgressConfig:
    """Progress tracking configuration settings."""
    show_bar: bool = True
    show_statistics: bool = True
    update_interval: int = 5


@dataclass
class AppConfig:
    """Main application configuration."""
    download: DownloadConfig = field(default_factory=DownloadConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    date_range: DateRangeConfig = field(default_factory=DateRangeConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    progress: ProgressConfig = field(default_factory=ProgressConfig)


class ConfigLoader:
    """
    Loads and validates configuration from YAML files.

    Provides default configuration and environment variable overrides.
    """

    DEFAULT_CONFIG_PATH = "configs/default_config.yaml"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path
        self.config = AppConfig()

    def load(self) -> AppConfig:
        """
        Load configuration from file and environment variables.

        Returns:
            Loaded AppConfig instance
        """
        # Load from file if specified
        if self.config_path:
            self._load_from_file(self.config_path)
        else:
            # Try default config
            if os.path.exists(self.DEFAULT_CONFIG_PATH):
                self._load_from_file(self.DEFAULT_CONFIG_PATH)

        # Apply environment variable overrides
        self._apply_env_overrides()

        # Validate configuration
        self._validate_config()

        return self.config

    def _load_from_file(self, config_path: str):
        """Load configuration from YAML file."""
        if not YAML_AVAILABLE:
            logger.warning("PyYAML not installed, skipping config file loading")
            return

        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)

            if not data:
                return

            # Parse each section
            if 'download' in data:
                self.config.download = DownloadConfig(**data['download'])
            if 'retry' in data:
                self.config.retry = RetryConfig(**data['retry'])
            if 'date_range' in data:
                self.config.date_range = DateRangeConfig(**data['date_range'])
            if 'logging' in data:
                self.config.logging = LoggingConfig(**data['logging'])
            if 'progress' in data:
                self.config.progress = ProgressConfig(**data['progress'])

            logger.info(f"Loaded configuration from {config_path}")

        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise

    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Output directory
        if os.environ.get('STORE_DIRECTORY'):
            self.config.download.output_directory = os.environ['STORE_DIRECTORY']

        # Log directory
        if os.environ.get('LOG_DIR'):
            self.config.logging.file = os.path.join(os.environ['LOG_DIR'], 'download.log')

        # Log level
        if os.environ.get('LOG_LEVEL'):
            self.config.logging.level = os.environ['LOG_LEVEL']

    def _validate_config(self):
        """Validate configuration values."""
        # Validate market type
        if self.config.download.market_type not in ('spot', 'um', 'cm'):
            raise ValueError(f"Invalid market_type: {self.config.download.market_type}")

        # Validate max_workers
        if self.config.download.max_workers < 1:
            raise ValueError(f"max_workers must be at least 1: {self.config.download.max_workers}")

        # Validate log level
        valid_log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        if self.config.logging.level.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.config.logging.level}")

        # Validate months
        if not all(1 <= m <= 12 for m in self.config.date_range.months):
            raise ValueError("Months must be between 1 and 12")

    def save(self, config_path: str):
        """
        Save current configuration to YAML file.

        Args:
            config_path: Path to save configuration file
        """
        if not YAML_AVAILABLE:
            logger.warning("PyYAML not installed, cannot save config file")
            return

        try:
            # Convert to dictionary
            data = {
                'download': {
                    'market_type': self.config.download.market_type,
                    'max_workers': self.config.download.max_workers,
                    'output_directory': self.config.download.output_directory,
                    'download_checksum': self.config.download.download_checksum,
                    'verify_checksum': self.config.download.verify_checksum,
                    'skip_monthly': self.config.download.skip_monthly,
                    'skip_daily': self.config.download.skip_daily,
                },
                'retry': {
                    'max_retries': self.config.retry.max_retries,
                    'initial_delay': self.config.retry.initial_delay,
                    'exponential_backoff': self.config.retry.exponential_backoff,
                },
                'date_range': {
                    'start_date': self.config.date_range.start_date,
                    'end_date': self.config.date_range.end_date,
                    'years': self.config.date_range.years,
                    'months': self.config.date_range.months,
                },
                'logging': {
                    'level': self.config.logging.level,
                    'file': self.config.logging.file,
                    'format': self.config.logging.format,
                },
                'progress': {
                    'show_bar': self.config.progress.show_bar,
                    'show_statistics': self.config.progress.show_statistics,
                    'update_interval': self.config.progress.update_interval,
                }
            }

            # Create directory if needed
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(config_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Saved configuration to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Convenience function to load configuration.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Loaded AppConfig instance
    """
    loader = ConfigLoader(config_path)
    return loader.load()
