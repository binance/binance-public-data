#!/usr/bin/env python3
"""
Binance Public Data - Option Downloader

Downloads options data from Binance.

Example:
    python3 scripts/download-option.py -s BTC-240301-50000-C -y 2024
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from binance_data_downloader.cli.commands import main


if __name__ == "__main__":
    sys.exit(main(parser_type='option'))
