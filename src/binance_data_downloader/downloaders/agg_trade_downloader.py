"""
Aggregated Trade Downloader

Downloads aggregated trade data from Binance.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class AggTradeDownloader(BaseDownloader):
    """
    Downloader for aggregated trade data.

    Supports all spot and futures markets.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "aggTrades"

    def supports_intervals(self) -> bool:
        """Aggregated trades do not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly aggregated trades filename.

        Example: BTCUSDT-aggTrades-2023-01.zip
        """
        return f"{symbol.upper()}-aggTrades-{year}-{month:02d}.zip"

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily aggregated trades filename.

        Example: BTCUSDT-aggTrades-2023-01-15.zip
        """
        return f"{symbol.upper()}-aggTrades-{date_str}.zip"
