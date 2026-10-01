# Migration Guide: Legacy Scripts to New Framework

This guide helps you migrate from the legacy Python scripts to the new enhanced framework while maintaining full backward compatibility.

---

## Quick Reference

| Legacy Script | New Equivalent | Notes |
|--------------|----------------|-------|
| `python/download-kline.py` | `scripts/download-all.py -d klines` | Use `-i` for intervals |
| `python/download-trade.py` | `scripts/download-all.py -d trades` | Same arguments |
| `python/download-aggTrade.py` | `scripts/download-all.py -d aggTrades` | Same arguments |
| `python/download-futures-indexPriceKlines.py` | `scripts/download-all.py -d indexPriceKlines` | Use `-i` for intervals |
| `python/download-futures-markPriceKlines.py` | `scripts/download-all.py -d markPriceKlines` | Use `-i` for intervals |
| `python/download-futures-premiumPriceKlines.py` | `scripts/download-all.py -d premiumIndexKlines` | Use `-i` for intervals |

---

## Backward Compatibility Guarantee

**All existing commands continue to work exactly as before:**

```bash
# These commands still work and produce identical results
python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -y 2024
python3 python/download-trade.py -t spot -s ETHUSDT -startDate 2023-01-01 -endDate 2023-12-31
python3 python/download-aggTrade.py -t um -s BTCUSDT -y 2023
```

**No changes required to your existing scripts or workflows.**

---

## Why Migrate to the New Framework?

### 1. **Multi-Data-Type Downloads**
Download multiple data types in a single command:

```bash
# Legacy: Run multiple commands
python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -y 2024
python3 python/download-trade.py -t spot -s BTCUSDT -y 2024
python3 python/download-aggTrade.py -t spot -s BTCUSDT -y 2024

# New: Single command
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines trades aggTrades -y 2024
```

### 2. **Access to New Data Types**
5 new data types not available in legacy scripts:

```bash
# Funding Rate (NEW)
python3 scripts/download-futures-fundingRate.py -t um -s BTCUSDT -y 2024

# Liquidation Snapshots (NEW)
python3 scripts/download-liquidation-snapshot.py -t cm -s ADAUSD_PERP -y 2024

# Book Ticker (NEW)
python3 scripts/download-book-ticker.py -t um -s BTCUSDT -y 2024

# Depth Data (NEW)
python3 scripts/download-depth.py -t spot -s BTCUSDT -y 2024

# Options Data (NEW)
python3 scripts/download-option.py -s BTC-240301-50000-C -y 2024
```

### 3. **Enhanced Features**

**Automatic Checksum Verification:**
```bash
# Legacy: Manual verification
sha256sum -c FILENAME.zip.CHECKSUM

# New: Automatic verification
python3 scripts/download-all.py -t spot -s BTCUSDT -y 2024 -c 1 -verify-checksum 1
```

**Config File Support:**
```bash
# Create config once
cat > my_config.yaml <<EOF
download:
  market_type: spot
  max_workers: 20
  download_checksum: true
  verify_checksum: true
date_range:
  years: [2024]
EOF

# Use config for all downloads
python3 scripts/download-all.py --config my_config.yaml -s BTCUSDT
```

**Better Logging:**
```bash
# New: Structured logging with levels
python3 scripts/download-all.py -t spot -s BTCUSDT -y 2024 -log-level DEBUG -log-file my_download.log
```

**Progress Statistics:**
```bash
# New: Detailed progress tracking and statistics
python3 scripts/download-all.py -t spot -s BTCUSDT -y 2024
# Output includes:
# - Progress bar per symbol
# - Success/failure/skip counts
# - Download speed statistics
# - Final summary report
```

---

## Step-by-Step Migration

### Step 1: Verify Current Commands Work

Ensure your existing commands still function:

```bash
python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -y 2024 -m 1
```

### Step 2: Try Equivalent New Command

```bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -i 1h -y 2024 -m 1
```

Compare the output files - they should be identical.

### Step 3: Gradually Adopt New Features

**Add checksum verification:**
```bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -y 2024 -c 1 -verify-checksum 1
```

**Increase parallelism:**
```bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -y 2024 -max_workers 20
```

**Enable detailed logging:**
```bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -y 2024 -log-level DEBUG
```

### Step 4: Create Config File (Optional)

For frequent downloads, create a config file:

```bash
cp configs/default_config.yaml my_config.yaml
# Edit my_config.yaml with your preferred settings
python3 scripts/download-all.py --config my_config.yaml -s BTCUSDT
```

### Step 5: Update Your Scripts

Update your automation scripts to use the new framework:

```bash
# Old script
#!/bin/bash
python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -y 2024

# New script
#!/bin/bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -i 1h -y 2024
```

---

## Argument Mapping

| Legacy Argument | New Argument | Notes |
|----------------|--------------|-------|
| `-t` | `-t` | Same (market type) |
| `-s` | `-s` | Same (symbols) |
| `-i` | `-i` | Same (intervals) |
| `-y` | `-y` | Same (years) |
| `-m` | `-m` | Same (months) |
| `-d` (dates) | `-d` (dates) | Same |
| `-startDate` | `-startDate` | Same |
| `-endDate` | `-endDate` | Same |
| `-skip-monthly` | `-skip-monthly` | Same |
| `-skip-daily` | `-skip-daily` | Same |
| `-folder` | `-folder` | Same |
| `-c` | `-c` | Same |
| `-max_workers` | `-max_workers` | Same (works for all data types now) |
| N/A | `-d` (data types) | **NEW** - Select data types |
| N/A | `--all-data` | **NEW** - Download all data types |
| N/A | `--config` | **NEW** - Use config file |
| N/A | `-verify-checksum` | **NEW** - Auto-verify checksums |
| N/A | `-log-level` | **NEW** - Set logging level |
| N/A | `-log-file` | **NEW** - Set log file path |

---

## Programmatic API Migration

### Legacy Approach (Direct Script Calls)

```python
import subprocess

# Call legacy script
subprocess.run([
    'python3', 'python/download-kline.py',
    '-t', 'spot',
    '-s', 'BTCUSDT',
    '-i', '1h',
    '-y', '2024'
])
```

### New Approach (Python API)

```python
from binance_data_downloader import KlineDownloader

# Direct Python API - better error handling and control
downloader = KlineDownloader(trading_type='spot', max_workers=10)

try:
    downloader.download_monthly(
        symbols=['BTCUSDT'],
        intervals=['1h'],
        years=['2024'],
        months=list(range(1, 13)),
        folder='/data/output',
        download_checksum=True,
        verify_checksum=True
    )
except Exception as e:
    print(f"Download failed: {e}")
```

---

## Common Migration Scenarios

### Scenario 1: Bulk Symbol Downloads

**Legacy:**
```bash
for symbol in BTCUSDT ETHUSDT BNBUSDT; do
    python3 python/download-kline.py -t spot -s $symbol -i 1h -y 2024
done
```

**New:**
```bash
# Single command for all symbols
python3 scripts/download-all.py -t spot -s BTCUSDT ETHUSDT BNBUSDT -d klines -i 1h -y 2024
```

### Scenario 2: Multiple Data Types

**Legacy:**
```bash
python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -y 2024
python3 python/download-trade.py -t spot -s BTCUSDT -y 2024
python3 python/download-aggTrade.py -t spot -s BTCUSDT -y 2024
```

**New:**
```bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines trades aggTrades -i 1h -y 2024
```

### Scenario 3: Date Range Filtering

**Legacy:**
```bash
python3 python/download-kline.py -t spot -s BTCUSDT -i 1h -startDate 2024-01-01 -endDate 2024-03-31
```

**New:**
```bash
python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -i 1h -startDate 2024-01-01 -endDate 2024-03-31
```

---

## Troubleshooting

### Issue: Command Not Found

**Problem:**
```bash
python3 scripts/download-all.py: command not found
```

**Solution:**
Make sure you're in the repository root directory:
```bash
cd /path/to/binance-public-data
python3 scripts/download-all.py -t spot -s BTCUSDT -y 2024
```

### Issue: Import Error

**Problem:**
```bash
ModuleNotFoundError: No module named 'binance_data_downloader'
```

**Solution:**
Install the package:
```bash
pip install -e .
```

### Issue: Config File Not Found

**Problem:**
```bash
File not found: configs/default_config.yaml
```

**Solution:**
Ensure you're in the repository root directory, or use absolute path:
```bash
python3 scripts/download-all.py --config /absolute/path/to/config.yaml -s BTCUSDT
```

---

## Rollback Plan

If you encounter issues with the new framework, you can always:

1. **Continue using legacy scripts** - They are unchanged and fully functional
2. **Report issues** - File a bug report on GitHub
3. **Check logs** - Review `logs/download.log` for detailed error information

---

## Summary

- **Legacy scripts continue to work** - No forced migration
- **New framework is additive** - Enhanced features, new data types
- **Gradual adoption** - Migrate at your own pace
- **Full backward compatibility** - Existing CLI arguments preserved

For questions or issues, please open an issue on the GitHub repository.
