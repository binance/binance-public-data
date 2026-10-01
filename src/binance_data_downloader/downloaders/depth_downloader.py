"""
Depth Downloader

Downloads order book depth data from Binance.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class DepthDownloader(BaseDownloader):
    """
    Downloader for order book depth data.

    Supports spot and USD-M (um) futures markets.
    Depth data provides the order book with bids and asks at various levels.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "depth"

    def supports_intervals(self) -> bool:
        """Depth data does not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Depth data is only available as daily files, not monthly.

        This method is not used for this data type.
        """
        raise NotImplementedError("Depth data is only available as daily files")

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily depth filename.

        Example: BTCUSDT-depth-2023-01-15.zip
        """
        return f"{symbol.upper()}-depth-{date_str}.zip"
