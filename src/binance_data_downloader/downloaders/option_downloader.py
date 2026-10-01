"""
Option Downloader

Downloads BVOLIndex (Bitcoin and Ethereum Volatility Index) data from Binance.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class OptionDownloader(BaseDownloader):
    """
    Downloader for BVOLIndex data.

    BVOLIndex provides Bitcoin and Ethereum volatility index data.
    Available symbols: BTCBVOLUSDT, ETHBVOLUSDT
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "option"

    def supports_intervals(self) -> bool:
        """BVOLIndex data does not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        BVOLIndex data is only available as daily files, not monthly.

        This method is not used for this data type.
        """
        raise NotImplementedError("BVOLIndex data is only available as daily files")

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily BVOLIndex filename.

        Example: BTCBVOLUSDT-BVOLIndex-2023-01-15.zip
        Format: SYMBOL-BVOLIndex-DATE.zip
        """
        return f"{symbol.upper()}-BVOLIndex-{date_str}.zip"
