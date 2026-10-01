#!/usr/bin/env python3
"""
Binance Public Data - Universal Downloader

This script can download any data type from Binance public data archive.
Supports downloading multiple data types simultaneously.

Examples:
    # Download klines only
    python3 scripts/download-all.py -t spot -s BTCUSDT -d klines -y 2024

    # Download multiple data types
    python3 scripts/download-all.py -t um -s BTCUSDT -d klines trades aggTrades -y 2024

    # Download all supported data types for a market
    python3 scripts/download-all.py -t spot --all-data -s BTCUSDT -y 2024

    # Use config file
    python3 scripts/download-all.py --config configs/default_config.yaml
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_data_downloader.cli.commands import main


if __name__ == "__main__":
    sys.exit(main(parser_type='download-all'))
