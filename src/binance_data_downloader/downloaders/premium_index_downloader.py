"""
Premium Index Kline Downloader

Downloads premium index kline data from Binance USD-M futures.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class PremiumIndexDownloader(BaseDownloader):
    """
    Downloader for premium index kline data.

    Supports USD-M (um) futures market only.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "premiumIndexKlines"

    def supports_intervals(self) -> bool:
        """Premium index klines support interval parameter."""
        return True

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly premium index kline filename.

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
        Format a daily premium index kline filename.

        Example: BTCUSDT-1h-2023-01-15.zip
        """
        return f"{symbol.upper()}-{interval}-{date_str}.zip"
