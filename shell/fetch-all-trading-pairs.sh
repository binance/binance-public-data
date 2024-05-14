#!/bin/bash

# Download all symbols from Spot, USD-M Futures and COIN-M Futures, into three separate files: `symbols.txt`, `um_symbols.txt` and `cm_symbols.txt`.
# Requires `jq` to be installed: https://stedolan.github.io/jq/

curl -s -H 'Content-Type: application/json'  https://api.binance.com/api/v3/exchangeInfo | jq -r '.symbols | sort_by(.symbol) | .[] | .symbol' > symbols.txt

curl -s -H 'Content-Type: application/json'  https://fapi.binance.com/fapi/v1/exchangeInfo | jq -r '.symbols | sort_by(.symbol) | .[] | .symbol' > um_symbols.txt

curl -s -H 'Content-Type: application/json'  https://dapi.binance.com/dapi/v1/exchangeInfo | jq -r '.symbols | sort_by(.symbol) | .[] | .symbol' > cm_symbols.txt