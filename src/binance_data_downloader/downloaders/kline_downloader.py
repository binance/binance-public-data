"""
Kline Downloader

Downloads kline (candlestick) data from Binance.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class KlineDownloader(BaseDownloader):
    """
    Downloader for kline (candlestick) data.

    Supports all spot and futures markets with various time intervals.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "klines"

    def supports_intervals(self) -> bool:
        """Klines support interval parameter."""
        return True

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly kline filename.

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
        Format a daily kline filename.

        Example: BTCUSDT-1h-2023-01-15.zip
        """
        return f"{symbol.upper()}-{interval}-{date_str}.zip"
