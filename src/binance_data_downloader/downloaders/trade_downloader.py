"""
Trade Downloader

Downloads individual trade data from Binance.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class TradeDownloader(BaseDownloader):
    """
    Downloader for individual trade data.

    Supports all spot and futures markets.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "trades"

    def supports_intervals(self) -> bool:
        """Trades do not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly trades filename.

        Example: BTCUSDT-trades-2023-01.zip
        """
        return f"{symbol.upper()}-trades-{year}-{month:02d}.zip"

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily trades filename.

        Example: BTCUSDT-trades-2023-01-15.zip
        """
        return f"{symbol.upper()}-trades-{date_str}.zip"
