#!/usr/bin/env python3
"""
Binance COIN-M Futures Premium Index Klines Downloader - NOT AVAILABLE

This script is a placeholder to indicate that premium index klines are NOT available
for COIN-M (cm) futures.

Premium Index Klines are only available for USD-M (um) futures.

Please use the USD-M premium index klines downloader instead:
    python3 scripts/download-futures-um-monthly-premiumIndexKlines.py

Or use the general futures premium index klines downloader with -t um:
    python3 python/download-futures-premiumPriceKlines.py -t um -s BTCUSDT

For COIN-M futures data, please use:
- download-futures-cm-monthly-klines.py
- download-futures-cm-monthly-indexPriceKlines.py
- download-futures-cm-monthly-markPriceKlines.py
"""

import sys


def main():
    """Main entry point."""
    print(__doc__)
    print("\n" + "="*70)
    print("ERROR: Premium Index Klines are only available for USD-M (um) futures")
    print("="*70)
    return 1


if __name__ == "__main__":
    sys.exit(main())
