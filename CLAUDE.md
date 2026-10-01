# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the official **Binance Public Data** repository - a toolkit for downloading historical market data from Binance's public data archive at `https://data.binance.vision/`.

The project has been refactored to provide both **legacy scripts** (for backward compatibility) and a **modern Python framework** with enhanced features.

### Data Types Available

**Spot Market:**
- klines (candlesticks), trades, aggregated trades, depth

**USD-M Futures (um):**
- klines, trades, aggregated trades, index price, mark price, premium index, funding rate, book ticker, depth

**COIN-M Futures (cm):**
- klines, trades, aggregated trades, index price, mark price, funding rate, liquidation snapshots, book ticker

**Options:**
- Options data

---

## Setup and Dependencies

```bash
# Install Python dependencies
pip install -r python/requirements.txt

# Or install the package with extras
pip install -e .

# Set output directory environment variable (optional, can override with -folder)
export STORE_DIRECTORY=/path/to/output
```

### Dependencies

- **Required**: `pandas>=1.3.0`, `certifi>=2021.5.30`
- **Optional**: `pyyaml>=5.4.1` (for config file support)
- **Development**: `pytest`, `pytest-cov`, `pytest-mock`, `black`, `flake8`, `mypy`

---

## Running Download Scripts

### Legacy Scripts (Backward Compatible)

The original scripts in `python/` continue to work exactly as before:

```bash
# Download klines
python3 python/download-kline.py -t spot -s ETHUSDT BTCUSDT -i 1h 1d -y 2023 2024

# Download trades
python3 python/download-trade.py -t spot -s ETHUSDT -startDate 2023-01-01 -endDate 2023-12-31

# Download aggregated trades
python3 python/download-aggTrade.py -t um -s BTCUSDT -y 2023

# Futures data
python3 python/download-futures-indexPriceKlines.py -t um -s BTCUSDT
python3 python/download-futures-markPriceKlines.py -t cm -s BTCUSD_PERP
python3 python/download-futures-premiumPriceKlines.py -t um -i 1m
```

### New Enhanced Scripts (Recommended)

The new scripts in `scripts/` provide additional features:

```bash
# Universal downloader - supports all data types
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines trades -y 2024

# Download all supported data types for a market
python3 scripts/download-all.py -t spot --all-data -s BTCUSDT -y 2024

# New data types
python3 scripts/download-futures-fundingRate.py -t um -s BTCUSDT -y 2024
python3 scripts/download-liquidation-snapshot.py -t cm -s ADAUSD_PERP -y 2024
python3 scripts/download-book-ticker.py -t um -s BTCUSDT -y 2024
python3 scripts/download-depth.py -t spot -s BTCUSDT -y 2024
python3 scripts/download-option.py -s BTC-240301-50000-C -y 2024

# Use config file
python3 scripts/download-all.py --config configs/default_config.yaml
```

### Common Arguments

| Argument | Purpose |
|----------|---------|
| `-t` | **Market type**: `spot`, `um` (USD-M Futures), or `cm` (COIN-M Futures) - **Required** |
| `-s` | Symbols to download (space-separated) - Default: all symbols |
| `-d` | Data types to download (for download-all.py) - Default: klines |
| `--all-data` | Download all supported data types for the market |
| `-i` | Kline intervals (e.g., `1m`, `1h`, `1d`) - Default: all intervals |
| `-y` | Years (e.g., `2023 2024`) - Default: 2020 to current year |
| `-m` | Months (1-12, space-separated) - Default: all months |
| `-d` | Specific dates in `YYYY-MM-DD` format - Default: from 2020-01-01 |
| `-startDate` | Start date range in `YYYY-MM-DD` format - Default: 2020-01-01 |
| `-endDate` | End date range in `YYYY-MM-DD` format - Default: current date |
| `-skip-monthly` | Set to `1` to skip monthly files |
| `-skip-daily` | Set to `1` to skip daily files |
| `-folder` | Output directory - Default: `STORE_DIRECTORY` env var or current directory |
| `-c` | Set to `1` to download `.CHECKSUM` files for data verification |
| `-verify-checksum` | Set to `1` to verify checksums after download |
| `-max_workers` | Number of threads for parallel downloads (default: 10) |
| `--config` | Path to YAML configuration file |
| `-log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `-log-file` | Log file path (default: logs/download.log) |

---

## New Architecture

### Directory Structure

```
J:\binance-public-data\
├── src/binance_data_downloader/    # New modular framework
│   ├── core/                        # Core components
│   │   ├── base_downloader.py       # Abstract base class
│   │   ├── data_type_config.py      # Data type registry
│   │   ├── retry_handler.py         # Retry mechanism
│   │   └── checksum_verifier.py     # Checksum verification
│   ├── downloaders/                 # Specific downloader implementations
│   ├── utils/                       # Utilities (path, date, file, logger)
│   ├── config/                      # Configuration management
│   └── cli/                         # Command-line interface
├── scripts/                         # New enhanced scripts
├── python/                          # Legacy scripts (PRESERVED)
├── shell/                           # Shell scripts (PRESERVED)
├── tests/                           # Unit and integration tests
├── configs/                         # Configuration files
└── logs/                            # Log output directory
```

### Core Components

**1. BaseDownloader (Abstract Base Class)**
- Location: `src/binance_data_downloader/core/base_downloader.py`
- All downloaders inherit from this class
- Provides `download_monthly()` and `download_daily()` methods
- Supports multi-threading via `-max_workers` parameter

**2. Data Type Configuration**
- Location: `src/binance_data_downloader/core/data_type_config.py`
- Central registry of all 12 data types
- `DataType` enum and `DataTypeSpec` dataclass
- `get_supported_data_types(market_type)` returns available data types

**3. Individual Downloaders**
- Location: `src/binance_data_downloader/downloaders/`
- Each downloader implements 4 abstract methods:
  - `get_data_type()` - Returns data type identifier
  - `supports_intervals()` - Whether intervals are supported
  - `format_monthly_filename()` - Monthly file naming
  - `format_daily_filename()` - Daily file naming

**4. Retry Handler**
- Location: `src/binance_data_downloader/core/retry_handler.py`
- Exponential backoff for failed downloads
- HTTP 404 errors are not retried (file doesn't exist)
- Configurable max retries and delay

**5. Checksum Verifier**
- Location: `src/binance_data_downloader/core/checksum_verifier.py`
- Cross-platform SHA256 verification
- Supports Linux (sha256sum), macOS (shasum), Windows (hashlib)

---

## Configuration File Support

Create a YAML config file to save frequently-used settings:

```yaml
# configs/my_config.yaml
download:
  market_type: spot
  max_workers: 10
  output_directory: /data/binance
  download_checksum: true
  verify_checksum: true

date_range:
  years: [2023, 2024]
  months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

logging:
  level: INFO
  file: logs/download.log

progress:
  show_bar: true
  show_statistics: true
```

Use it with: `python3 scripts/download-all.py --config configs/my_config.yaml`

---

## Programmatic API

You can also use the downloaders directly in Python code:

```python
from binance_data_downloader import KlineDownloader

# Initialize downloader
downloader = KlineDownloader(trading_type='spot', max_workers=10)

# Download monthly data
downloader.download_monthly(
    symbols=['BTCUSDT', 'ETHUSDT'],
    intervals=['1h', '1d'],
    years=['2024'],
    months=list(range(1, 13)),
    folder='/data/output',
    download_checksum=True,
    verify_checksum=True
)

# Download daily data
downloader.download_daily(
    symbols=['BTCUSDT'],
    intervals=['1h'],
    dates=['2024-01-01', '2024-01-02'],
    folder='/data/output'
)
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/binance_data_downloader --cov-report=html

# Run specific test
pytest tests/unit/test_data_type_config.py -v
```

---

## Cross-Platform Compatibility

The scripts work on:
- **Linux**: Uses `sha256sum` for checksum verification
- **macOS**: Uses `shasum -a 256` for checksum verification
- **Windows**: Uses Python `hashlib` for checksum verification

---

## Key Implementation Details

### Legacy Scripts (python/)
- **Location**: `python/download-*.py`
- **Dependencies**: `python/utility.py`, `python/enums.py`
- **Behavior**: Preserved exactly as before
- **Status**: Do NOT modify - maintain backward compatibility

### New Framework (src/binance_data_downloader/)
- **Architecture**: Modular, extensible, testable
- **Code reuse**: 90%+ reduction in code duplication
- **Features**: Multi-threading, retry, checksum verification, logging, progress tracking
- **Status**: Active development - add new features here

### Data URL Structure

```
https://data.binance.vision/
├── data/
│   ├── spot/
│   │   ├── monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{YEAR}-{MONTH}.zip
│   │   ├── daily/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{DATE}.zip
│   │   └── daily/depth/{SYMBOL}/{SYMBOL}-depth-{DATE}.zip
│   └── futures/
│       ├── um/ (USD-M Futures)
│       │   ├── monthly/klines/
│       │   ├── monthly/fundingRate/
│       │   └── daily/bookTicker/
│       └── cm/ (COIN-M Futures)
│           ├── monthly/klines/
│           └── daily/liquidationSnapshot/
```

### Error Handling

- **HTTP 404**: File not found, logged and skipped (not an error)
- **Network errors**: Retried with exponential backoff (max 3 retries)
- **Corrupted downloads**: Detected via checksum verification if enabled

---

## Migration Notes

When adding new features or modifying downloaders:

1. **New data types**: Add to `core/data_type_config.py`, then create downloader in `downloaders/`
2. **CLI changes**: Modify `cli/argument_parser.py` and `cli/commands.py`
3. **Config options**: Update `config/config_loader.py` and `configs/default_config.yaml`
4. **DO NOT modify**: Legacy scripts in `python/` directory (maintain backward compatibility)
5. **Always add tests**: Unit tests in `tests/unit/`, integration tests in `tests/integration/`

See `MIGRATION.md` for detailed migration guide from legacy scripts to new framework.
