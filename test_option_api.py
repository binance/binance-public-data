#!/usr/bin/env python3
"""Test option API endpoint."""

import urllib.request
import json

# Test the option API endpoint
print('Testing Option API endpoint...')
try:
    response = urllib.request.urlopen('https://eapi.binance.com/eapi/v1/exchangeInfo', timeout=10).read()
    data = json.loads(response)

    # Show symbol info
    symbols_count = len(data.get("symbols", []))
    print('Symbols returned: ' + str(symbols_count))
    print('')
    print('Available option symbols:')
    for symbol in data.get("symbols", []):
        print('  ' + symbol["symbol"])

except Exception as e:
    print('Error: ' + str(e))
