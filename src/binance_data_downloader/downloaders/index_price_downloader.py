"""
Index Price Kline Downloader

Downloads index price kline data from Binance futures.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class IndexPriceDownloader(BaseDownloader):
    """
    Downloader for index price kline data.

    Supports USD-M (um) and COIN-M (cm) futures markets.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "indexPriceKlines"

    def supports_intervals(self) -> bool:
        """Index price klines support interval parameter."""
        return True

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly index price kline filename.

        Example: BTCUSDT-1h-2023-01.zip
        """
        return f"{symbol.upper()}-{interval}-{year}-{month:02d}.zip"

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily index price kline filename.

        Example: BTCUSDT-1h-2023-01-15.zip
        """
        return f"{symbol.upper()}-{interval}-{date_str}.zip"
