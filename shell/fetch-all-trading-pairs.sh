#!/bin/bash

# simple scripts to download all trading symbols
# jq is required

curl -s -H 'Content-Type: application/json'  https://api.binance.com/api/v3/exchangeInfo | jq -r '.symbols | sort_by(.symbol) | .[] | .symbol' > symbol.txt
