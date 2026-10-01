"""
Book Ticker Downloader

Downloads book ticker (best bid/ask price) data from Binance.
"""

from typing import Optional

from ..core.base_downloader import BaseDownloader


class BookTickerDownloader(BaseDownloader):
    """
    Downloader for book ticker data.

    Supports USD-M (um) and COIN-M (cm) futures markets.
    Book ticker provides the best bid price, best ask price, and quantities.
    """

    def get_data_type(self) -> str:
        """Return the data type identifier."""
        return "bookTicker"

    def supports_intervals(self) -> bool:
        """Book tickers do not support interval parameter."""
        return False

    def format_monthly_filename(
        self,
        symbol: str,
        interval: Optional[str],
        year: str,
        month: int
    ) -> str:
        """
        Book tickers are only available as daily files, not monthly.

        This method is not used for this data type.
        """
        raise NotImplementedError("Book tickers are only available as daily files")

    def format_daily_filename(
        self,
        symbol: str,
        interval: Optional[str],
        date_str: str
    ) -> str:
        """
        Format a daily book ticker filename.

        Example: BTCUSDT-bookTicker-2023-01-15.zip
        """
        return f"{symbol.upper()}-bookTicker-{date_str}.zip"
