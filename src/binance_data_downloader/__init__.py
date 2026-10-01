"""
Binance Public Data Downloader

A comprehensive toolkit for downloading historical market data from Binance's
public data archive at https://data.binance.vision/

This package provides:
- Support for 12 data types (klines, trades, aggTrades, index/mark/premium price klines,
  funding rate, liquidation snapshots, book ticker, depth, options)
- Multi-threaded downloads with configurable worker count
- Automatic retry with exponential backoff
- SHA256 checksum verification
- Progress tracking and detailed logging
- Configuration file support
- Both programmatic API and CLI tools

Example usage (CLI):
    # Download klines for specific symbol
    python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -y 2024

    # Download all data types
    python3 scripts/download-all.py -t spot --all-data -s BTCUSDT -y 2024

Example usage (Python API):
    from binance_data_downloader.downloaders import KlineDownloader

    downloader = KlineDownloader(trading_type='spot', max_workers=10)
    downloader.download_monthly(
        symbols=['BTCUSDT', 'ETHUSDT'],
        intervals=['1h', '1d'],
        years=['2024'],
        months=list(range(1, 13))
    )
"""

__version__ = '1.0.0'
__author__ = 'Binance'
__license__ = 'MIT'

# Core exports
from .core.base_downloader import BaseDownloader
from .core.data_type_config import (
    DataType,
    DataTypeSpec,
    get_data_type_spec,
    get_supported_data_types,
    get_all_data_types,
)
from .core.retry_handler import RetryHandler
from .core.checksum_verifier import ChecksumVerifier

# Downloader exports
from .downloaders.kline_downloader import KlineDownloader
from .downloaders.trade_downloader import TradeDownloader
from .downloaders.agg_trade_downloader import AggTradeDownloader
from .downloaders.index_price_downloader import IndexPriceDownloader
from .downloaders.mark_price_downloader import MarkPriceDownloader
from .downloaders.premium_index_downloader import PremiumIndexDownloader
from .downloaders.funding_rate_downloader import FundingRateDownloader
from .downloaders.liquidation_snapshot_downloader import LiquidationSnapshotDownloader
from .downloaders.book_ticker_downloader import BookTickerDownloader
from .downloaders.depth_downloader import DepthDownloader
from .downloaders.option_downloader import OptionDownloader

# Utility exports
from .utils.date_utils import (
    convert_to_date_object,
    generate_date_range,
    get_default_start_date,
    get_default_end_date,
)
from .utils.file_operations import FileDownloader, get_all_symbols
from .utils.logger_setup import setup_logger, get_logger
from .utils.progress_tracker import ProgressTracker, MultiProgressTracker

# Config exports
from .config.config_loader import ConfigLoader, AppConfig, load_config

__all__ = [
    # Version
    '__version__',
    '__author__',
    '__license__',

    # Core
    'BaseDownloader',
    'DataType',
    'DataTypeSpec',
    'get_data_type_spec',
    'get_supported_data_types',
    'get_all_data_types',
    'RetryHandler',
    'ChecksumVerifier',

    # Downloaders
    'KlineDownloader',
    'TradeDownloader',
    'AggTradeDownloader',
    'IndexPriceDownloader',
    'MarkPriceDownloader',
    'PremiumIndexDownloader',
    'FundingRateDownloader',
    'LiquidationSnapshotDownloader',
    'BookTickerDownloader',
    'DepthDownloader',
    'OptionDownloader',

    # Utilities
    'convert_to_date_object',
    'generate_date_range',
    'get_default_start_date',
    'get_default_end_date',
    'FileDownloader',
    'get_all_symbols',
    'setup_logger',
    'get_logger',
    'ProgressTracker',
    'MultiProgressTracker',

    # Config
    'ConfigLoader',
    'AppConfig',
    'load_config',
]
