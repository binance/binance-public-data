#!/usr/bin/env python3
"""
Binance COIN-M Futures Daily Book Depth Downloader

NOTICE: Depth data is NOT available for COIN-M Futures (cm).
This script is provided for reference but will not work with cm market.
For depth data, please use spot market instead.

For alternative cm data, consider using:
- download-futures-cm-daily-bookTicker.py (best bid/ask prices)
- download-futures-cm-daily-klines.py (OHLCV data)

If you need depth data, use:
- scripts/download-depth.py -t spot (for spot market depth data)

This script is kept as a placeholder for future availability.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    print("=" * 70)
    print("ERROR: Depth data is NOT available for COIN-M Futures (cm)")
    print("=" * 70)
    print()
    print("According to Binance Public Data structure:")
    print("- Spot market: supports depth data")
    print("- USD-M Futures (um): supports depth data")
    print("- COIN-M Futures (cm): does NOT support depth data")
    print()
    print("Available alternatives for cm market:")
    print("  - download-futures-cm-daily-bookTicker.py (best bid/ask)")
    print("  - download-futures-cm-daily-klines.py (OHLCV candles)")
    print()
    print("For depth data, use spot market:")
    print("  - scripts/download-depth.py -t spot -s BTCUSDT")
    print()
    return 1

if __name__ == "__main__":
    sys.exit(main())
