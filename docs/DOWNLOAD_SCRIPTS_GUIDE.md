# Download Scripts Guide

This guide provides comprehensive documentation for all download scripts in the Binance Public Data repository.

## Table of Contents

- [Quick Start](#quick-start)
- [Script Reference by Market](#script-reference-by-market)
  - [Spot Market Scripts](#spot-market-scripts)
  - [Futures-UM Market Scripts](#futures-um-market-scripts)
  - [Futures-CM Market Scripts](#futures-cm-market-scripts)
  - [Options Market Scripts](#options-market-scripts)
- [Universal Downloader](#universal-downloader)
- [Parameter Reference](#parameter-reference)
- [Tips and Best Practices](#tips-and-best-practices)
- [File Location Information](#file-location-information)

---

## Quick Start

### Installation

```bash
# Install Python dependencies
pip install -r python/requirements.txt

# Or install the package
pip install -e .

# Set output directory (optional)
export STORE_DIRECTORY=/path/to/output
```

### Basic Usage

```bash
# Download spot klines for a specific symbol
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -y 2024

# Download futures funding rate
python3 scripts/download-futures-fundingRate.py -s BTCUSDT -y 2024

# Download multiple data types at once
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines trades aggTrades -y 2024
```

---

## Script Reference by Market

### Spot Market Scripts

The spot market supports 4 data types: **klines**, **trades**, **aggTrades**, and **depth**.

| Script Name | Data Type | Intervals Support | Monthly | Daily |
|-------------|-----------|-------------------|---------|-------|
| `download-spot-monthly-klines.py` | Klines | Yes (1m, 15m, 1h, 4h, 8h) | ✓ | - |
| `download-depth.py` | Depth | No | - | ✓ |
| `download-all.py` | All spot types | Varies | ✓ | ✓ |

#### Klines (Candlestick Data)

**Script:** `download-spot-monthly-klines.py`

**Features:**
- Monthly data only
- Supports multiple intervals: 1m, 15m, 1h, 4h, 8h
- Auto-skips existing files
- 10-thread concurrent downloads

**Usage Examples:**

```bash
# Download with default intervals (1m, 15m, 1h, 4h, 8h)
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT

# Download specific intervals
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -i 1m 1h

# Download for specific year
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -y 2024

# Download multiple symbols
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT ETHUSDT

# Download specific months
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -y 2024 -m 1 2 3

# Custom output folder
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -folder /data/binance
```

**Common Patterns:**

```bash
# Download all intervals for current year
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -y $(date +%Y)

# Download hourly data for multiple symbols
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT ETHUSDT BNBUSDT -i 1h -y 2023 2024

# Download with debug logging
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -log-level DEBUG
```

#### Depth (Order Book)

**Script:** `download-depth.py`

**Features:**
- Daily data only
- No interval support
- Full order book depth snapshots

**Usage Examples:**

```bash
# Download depth data for a symbol
python3 scripts/download-depth.py -s BTCUSDT -y 2024

# Download for specific date range
python3 scripts/download-depth.py -s BTCUSDT -startDate 2024-01-01 -endDate 2024-01-31

# Download multiple symbols
python3 scripts/download-depth.py -s BTCUSDT ETHUSDT -y 2024
```

---

### Futures-UM Market Scripts

The USD-M Futures market supports 9 data types: **klines**, **trades**, **aggTrades**, **indexPriceKlines**, **markPriceKlines**, **premiumIndexKlines**, **fundingRate**, **bookTicker**, and **depth**.

| Script Name | Data Type | Intervals Support | Monthly | Daily |
|-------------|-----------|-------------------|---------|-------|
| `download-futures-fundingRate.py` | Funding Rate | No | ✓ | ✗ |
| `download-book-ticker.py` | Book Ticker | No | - | ✓ |
| `download-depth.py` | Depth | No | - | ✓ |
| `download-all.py` | All UM types | Varies | ✓ | ✓ |

#### Funding Rate

**Script:** `download-futures-fundingRate.py`

**Features:**
- Monthly data only (daily not available)
- Auto-detects available date range
- Skips downloading if local data exists
- Supports both UM and CM futures

**Usage Examples:**

```bash
# Download with auto-detected date range (recommended)
python3 scripts/download-futures-fundingRate.py -s BTCUSDT

# Download for specific year/month range
python3 scripts/download-futures-fundingRate.py -s BTCUSDT -y 2023 2024

# Download multiple symbols
python3 scripts/download-futures-fundingRate.py -s BTCUSDT ETHUSDT

# Download for COIN-M futures
python3 scripts/download-futures-fundingRate.py -t cm -s ADAUSD_PERP

# Specify custom output folder
python3 scripts/download-futures-fundingRate.py -s BTCUSDT -folder /data/binance

# Download specific months
python3 scripts/download-futures-fundingRate.py -s BTCUSDT -y 2024 -m 1 2 3
```

**Common Patterns:**

```bash
# Download all USD-M futures funding rates
python3 scripts/download-futures-fundingRate.py -t um

# Download for a specific date range
python3 scripts/download-futures-fundingRate.py -s BTCUSDT -y 2024 -m 6 7 8

# Force re-download even if files exist
python3 scripts/download-futures-fundingRate.py -s BTCUSDT --no-skip-existing
```

#### Book Ticker (Best Bid/Ask)

**Script:** `download-book-ticker.py`

**Features:**
- Daily data only
- Best bid/ask prices
- UM and CM futures support

**Usage Examples:**

```bash
# Download for USD-M futures
python3 scripts/download-book-ticker.py -t um -s BTCUSDT -y 2024

# Download for COIN-M futures
python3 scripts/download-book-ticker.py -t cm -s ADAUSD_PERP -y 2024

# Download for specific date range
python3 scripts/download-book-ticker.py -t um -s BTCUSDT -startDate 2024-01-01 -endDate 2024-01-31

# Download multiple symbols
python3 scripts/download-book-ticker.py -t um -s BTCUSDT ETHUSDT -y 2024
```

#### Other UM Data Types

Use the **Universal Downloader** (`download-all.py`) for these data types:

- **Klines** - Candlestick data with intervals
- **Trades** - Individual trade executions
- **AggTrades** - Aggregated trades
- **Index Price Klines** - Index price candlesticks
- **Mark Price Klines** - Mark price candlesticks
- **Premium Index Klines** - Premium index candlesticks

**Examples:**

```bash
# Download klines
python3 scripts/download-all.py -t um -s BTCUSDT -d klines -i 1h -y 2024

# Download multiple data types
python3 scripts/download-all.py -t um -s BTCUSDT -d klines trades aggTrades -y 2024

# Download index and mark price
python3 scripts/download-all.py -t um -s BTCUSDT -d indexPriceKlines markPriceKlines -i 1h -y 2024

# Download premium index
python3 scripts/download-all.py -t um -s BTCUSDT -d premiumIndexKlines -i 1d -y 2024

# Download all UM data types
python3 scripts/download-all.py -t um --all-data -s BTCUSDT -y 2024
```

---

### Futures-CM Market Scripts

The COIN-M Futures market supports 7 data types: **klines**, **trades**, **aggTrades**, **indexPriceKlines**, **markPriceKlines**, **fundingRate**, and **liquidationSnapshot**.

| Script Name | Data Type | Intervals Support | Monthly | Daily |
|-------------|-----------|-------------------|---------|-------|
| `download-futures-fundingRate.py` | Funding Rate | No | ✓ | ✗ |
| `download-liquidation-snapshot.py` | Liquidation Snapshot | No | - | ✓ |
| `download-book-ticker.py` | Book Ticker | No | - | ✓ |
| `download-all.py` | All CM types | Varies | ✓ | ✓ |

#### Liquidation Snapshot

**Script:** `download-liquidation-snapshot.py`

**Features:**
- Daily data only
- COIN-M futures exclusive
- Liquidation order snapshots

**Usage Examples:**

```bash
# Download liquidation snapshots
python3 scripts/download-liquidation-snapshot.py -t cm -s ADAUSD_PERP -y 2024

# Download for specific date range
python3 scripts/download-liquidation-snapshot.py -t cm -s ADAUSD_PERP -startDate 2024-01-01 -endDate 2024-01-31

# Download multiple symbols
python3 scripts/download-liquidation-snapshot.py -t cm -s ADAUSD_PERP BCHUSD_PERP -y 2024
```

#### Other CM Data Types

Use the **Universal Downloader** (`download-all.py`) for these data types:

- **Klines** - Candlestick data with intervals
- **Trades** - Individual trade executions
- **AggTrades** - Aggregated trades
- **Index Price Klines** - Index price candlesticks
- **Mark Price Klines** - Mark price candlesticks

**Examples:**

```bash
# Download klines
python3 scripts/download-all.py -t cm -s ADAUSD_PERP -d klines -i 1h -y 2024

# Download multiple data types
python3 scripts/download-all.py -t cm -s ADAUSD_PERP -d klines trades aggTrades -y 2024

# Download all CM data types
python3 scripts/download-all.py -t cm --all-data -s ADAUSD_PERP -y 2024
```

---

### Options Market Scripts

| Script Name | Data Type | Intervals Support | Monthly | Daily |
|-------------|-----------|-------------------|---------|-------|
| `download-option.py` | Options Data | No | - | ✓ |

#### Options Data

**Script:** `download-option.py`

**Features:**
- Daily data only
- Options market data
- Requires option symbol format

**Usage Examples:**

```bash
# Download options data
python3 scripts/download-option.py -s BTC-240301-50000-C -y 2024

# Download multiple options
python3 scripts/download-option.py -s BTC-240301-50000-C BTC-240301-55000-C -y 2024

# Download for specific date range
python3 scripts/download-option.py -s BTC-240301-50000-C -startDate 2024-01-01 -endDate 2024-01-31
```

**Option Symbol Format:** `{UNDERLYING}-{EXPIRATION}-{STRIKE}-{TYPE}`
- Example: `BTC-240301-50000-C`
  - Underlying: BTC
  - Expiration: 240301 (March 1, 2024)
  - Strike: 50000
  - Type: C (Call) or P (Put)

---

## Universal Downloader

The `download-all.py` script is a powerful universal downloader that supports all data types across all markets.

### Key Features

- Download multiple data types in one command
- Support for all markets (spot, um, cm)
- Config file support
- Download all data types with `--all-data` flag

### Usage Examples

```bash
# Download single data type
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -y 2024

# Download multiple data types
python3 scripts/download-all.py -t um -s BTCUSDT -d klines trades aggTrades -y 2024

# Download all supported data types for a market
python3 scripts/download-all.py -t spot --all-data -s BTCUSDT -y 2024

# Specify intervals for klines
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -i 1h 1d -y 2024

# Use config file
python3 scripts/download-all.py --config configs/default_config.yaml

# Download with date range
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -startDate 2024-01-01 -endDate 2024-12-31

# Download daily data
python3 scripts/download-all.py -t spot -s BTCUSDT -d trades -startDate 2024-01-01 -endDate 2024-01-31
```

---

## Parameter Reference

### Common Parameters

| Parameter | Short | Description | Default | Examples |
|-----------|-------|-------------|---------|----------|
| `--type` | `-t` | Market type | Required | `spot`, `um`, `cm` |
| `--symbols` | `-s` | Trading symbols | All available | `BTCUSDT ETHUSDT` |
| `--data-types` | `-d` | Data types | `klines` | `klines trades aggTrades` |
| `--intervals` | `-i` | Kline intervals | All intervals | `1m 1h 1d` |
| `--years` | `-y` | Years to download | 2020-current | `2023 2024` |
| `--months` | `-m` | Months to download | All (1-12) | `1 2 3` |
| `--startDate` | - | Start date | 2020-01-01 | `2024-01-01` |
| `--endDate` | - | End date | Current date | `2024-12-31` |
| `--folder` | - | Output directory | STORE_DIRECTORY or `.` | `/data/binance` |
| `--max-workers` | - | Concurrent threads | 10 | `20` |
| `--skip-monthly` | - | Skip monthly files | 0 (download) | `1` to skip |
| `--skip-daily` | - | Skip daily files | 0 (download) | `1` to skip |
| `--download-checksum` | `-c` | Download checksum files | 0 (no) | `1` to download |
| `--verify-checksum` | - | Verify checksums | 0 (no) | `1` to verify |
| `--log-level` | - | Logging level | INFO | `DEBUG INFO WARNING ERROR` |
| `--log-file` | - | Log file path | logs/download.log | `/var/log/binance.log` |
| `--config` | - | Config file path | None | `configs/my_config.yaml` |
| `--all-data` | - | Download all data types | False | Flag to enable |

### Valid Intervals

For data types that support intervals (klines, indexPriceKlines, markPriceKlines, premiumIndexKlines):

- **1m** - 1 minute
- **3m** - 3 minutes
- **5m** - 5 minutes
- **15m** - 15 minutes
- **30m** - 30 minutes
- **1h** - 1 hour
- **2h** - 2 hours
- **4h** - 4 hours
- **6h** - 6 hours
- **8h** - 8 hours
- **12h** - 12 hours
- **1d** - 1 day
- **3d** - 3 days
- **1w** - 1 week
- **1M** - 1 month

---

## Tips and Best Practices

### 1. Choose the Right Script

- **Use specialized scripts** (e.g., `download-futures-fundingRate.py`) for specific data types - they have optimized features
- **Use universal downloader** (`download-all.py`) when downloading multiple data types simultaneously
- **Use config files** for complex, frequently-used download patterns

### 2. Performance Optimization

```bash
# Increase concurrent threads for faster downloads
python3 scripts/download-all.py -t spot -s BTCUSDT -max_workers 20

# Download monthly data instead of daily for faster speeds
python3 scripts/download-all.py -t spot -s BTCUSDT -skip-daily 1

# Use multiple symbols in one command
python3 scripts/download-all.py -t spot -s BTCUSDT ETHUSDT BNBUSDT -y 2024
```

### 3. Data Management

```bash
# Skip existing files to save time
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT  # Auto-skips by default

# Verify data integrity with checksums
python3 scripts/download-all.py -t spot -s BTCUSDT -download-checksum 1 -verify-checksum 1

# Use custom output folder for organization
python3 scripts/download-all.py -t spot -s BTCUSDT -folder /data/binance/spot/2024
```

### 4. Date Range Selection

```bash
# Use years for monthly data
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -y 2023 2024

# Use specific dates for daily data
python3 scripts/download-all.py -t spot -s BTCUSDT -d trades -startDate 2024-01-01 -endDate 2024-01-31

# Combine year and month for precision
python3 scripts/download-spot-monthly-klines.py -s BTCUSDT -y 2024 -m 1 2 3
```

### 5. Debugging

```bash
# Enable debug logging
python3 scripts/download-all.py -t spot -s BTCUSDT -log-level DEBUG

# Specify log file location
python3 scripts/download-all.py -t spot -s BTCUSDT -log-file /tmp/download.log
```

### 6. Automation

```bash
# Create a cron job for daily updates
# Add to crontab: 0 2 * * * cd /path/to/binance-public-data && python3 scripts/download-all.py -t spot -s BTCUSDT -y $(date +%Y) -m $(date +%m)

# Use bash scripts for bulk downloads
for symbol in BTCUSDT ETHUSDT BNBUSDT; do
    python3 scripts/download-spot-monthly-klines.py -s $symbol -y 2024
done
```

---

## File Location Information

### URL Structure

```
https://data.binance.vision/
├── data/
│   ├── spot/                              # Spot market
│   │   ├── monthly/
│   │   │   ├── klines/{SYMBOL}/{INTERVAL}/
│   │   │   │   └── {SYMBOL}-{INTERVAL}-{YEAR}-{MONTH}.zip
│   │   │   ├── trades/{SYMBOL}/
│   │   │   │   └── {SYMBOL}-trades-{YEAR}-{MONTH}.zip
│   │   │   └── aggTrades/{SYMBOL}/
│   │   │       └── {SYMBOL}-aggTrades-{YEAR}-{MONTH}.zip
│   │   └── daily/
│   │       ├── klines/{SYMBOL}/{INTERVAL}/
│   │       │   └── {SYMBOL}-{INTERVAL}-{DATE}.zip
│   │       ├── trades/{SYMBOL}/
│   │       │   └── {SYMBOL}-trades-{DATE}.zip
│   │       ├── aggTrades/{SYMBOL}/
│   │       │   └── {SYMBOL}-aggTrades-{DATE}.zip
│   │       └── depth/{SYMBOL}/
│   │           └── {SYMBOL}-depth-{DATE}.zip
│   └── futures/                           # Futures market
│       ├── um/                            # USD-M Futures
│       │   ├── monthly/
│       │   │   ├── klines/{SYMBOL}/{INTERVAL}/
│       │   │   ├── fundingRate/{SYMBOL}/
│       │   │   │   └── {SYMBOL}-fundingRate-{YEAR}-{MONTH}.zip
│       │   │   ├── indexPriceKlines/{SYMBOL}/{INTERVAL}/
│       │   │   ├── markPriceKlines/{SYMBOL}/{INTERVAL}/
│       │   │   └── premiumIndexKlines/{SYMBOL}/{INTERVAL}/
│       │   └── daily/
│       │       ├── bookTicker/{SYMBOL}/
│       │       │   └── {SYMBOL}-bookTicker-{DATE}.zip
│       │       ├── depth/{SYMBOL}/
│       │       └── (other types similar to spot)
│       └── cm/                            # COIN-M Futures
│           ├── monthly/
│           │   └── (similar structure to um)
│           └── daily/
│               ├── liquidationSnapshot/{SYMBOL}/
│               │   └── {SYMBOL}-liquidationSnapshot-{DATE}.zip
│               └── bookTicker/{SYMBOL}/
└── data/derivatives/                      # Options
    └── monthly/BVOLIndex/
        └── {SYMBOL}/
            └── {SYMBOL}-{YEAR}-{MONTH}.zip
```

### Local File Organization

Downloaded files maintain the same structure locally:

```
{STORE_DIRECTORY}/
├── spot/
│   ├── monthly/
│   │   └── klines/
│   │       └── BTCUSDT/
│   │           └── 1h/
│   │               └── BTCUSDT-1h-2024-01.zip
│   └── daily/
│       └── trades/
│           └── BTCUSDT/
│               └── BTCUSDT-trades-2024-01-01.zip
└── futures/
    └── um/
        ├── monthly/
        │   └── fundingRate/
        │       └── BTCUSDT/
        │           └── BTCUSDT-fundingRate-2024-01.zip
        └── daily/
            └── bookTicker/
                └── BTCUSDT/
                    └── BTCUSDT-bookTicker-2024-01-01.zip
```

### Monthly vs Daily Files

**When to use Monthly:**
- Historical data downloads
- Backtesting with historical data
- Data analysis and research
- When downloading large date ranges

**When to use Daily:**
- Recent data updates
- Incremental updates
- Specific date analysis
- When monthly files are not available

**Note:** Some data types only have monthly OR daily files:
- **Funding Rate**: Monthly only
- **Liquidation Snapshot**: Daily only
- **Book Ticker**: Daily only
- **Depth**: Daily only

---

## Additional Resources

- **Main README:** [../README.md](../README.md)
- **Migration Guide:** [MIGRATION.md](../MIGRATION.md)
- **Project Instructions:** [../CLAUDE.md](../CLAUDE.md)
- **Legacy Scripts:** See `python/` directory for original scripts
- **Configuration:** See `configs/default_config.yaml` for config file examples

---

## Troubleshooting

### Common Issues

**Issue:** "HTTP 404 errors in logs"
- **Solution:** This is normal - it means a file doesn't exist on the server yet (e.g., future dates)

**Issue:** "Download is slow"
- **Solution:** Increase `-max_workers` parameter (default: 10)

**Issue:** "Out of memory"
- **Solution:** Download fewer symbols at once, reduce `-max_workers`

**Issue:** "Checksum verification failed"
- **Solution:** Re-download the file with `--no-skip-existing` flag

**Issue:** "Connection timeout"
- **Solution:** The script automatically retries with exponential backoff (max 3 retries)

### Getting Help

For issues, questions, or contributions:
1. Check this documentation
2. Review example commands in each script's docstring
3. Enable debug logging: `-log-level DEBUG`
4. Check log files: `logs/download.log`

---

## Version Information

- **Documentation Version:** 1.0
- **Last Updated:** 2025-01-18
- **Compatible with:** Binance Public Data repository (master branch)
