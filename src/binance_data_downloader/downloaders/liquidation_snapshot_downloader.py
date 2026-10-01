"""
Liquidation Snapshot Downloader

Downloads liquidation snapshot data from Binance futures.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class LiquidationSnapshotDownloader(BaseDownloader):
    """
    Downloader for liquidation snapshot data.

    Supports COIN-M (cm) futures market only.
    Liquidation snapshots show the state of forced liquidations.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "liquidationSnapshot"

    def supports_intervals(self) -> bool:
        """Liquidation snapshots do not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Liquidation snapshots are only available as daily files, not monthly.

        This method is not used for this data type.
        """
        raise NotImplementedError("Liquidation snapshots are only available as daily files")

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily liquidation snapshot filename.

        Example: BTCUSD_PERP-liquidationSnapshot-2023-01-15.zip
        """
        return f"{symbol.upper()}-liquidationSnapshot-{date_str}.zip"
