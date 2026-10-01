"""
Funding Rate Downloader

Downloads funding rate history data from Binance futures.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class FundingRateDownloader(BaseDownloader):
    """
    Downloader for funding rate history data.

    Supports USD-M (um) and COIN-M (cm) futures markets.
    Funding rates are published daily and determine the periodic payments
    between long and short position holders.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "fundingRate"

    def supports_intervals(self) -> bool:
        """Funding rates do not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Format a monthly funding rate filename.

        Example: BTCUSDT-fundingRate-2023-01.zip
        """
        return f"{symbol.upper()}-fundingRate-{year}-{month:02d}.zip"

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily funding rate filename.

        Example: BTCUSDT-fundingRate-2023-01-15.zip
        """
        return f"{symbol.upper()}-fundingRate-{date_str}.zip"
