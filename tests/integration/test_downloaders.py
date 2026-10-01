"""
Integration tests for downloaders.

These tests verify the downloaders can be instantiated and configured correctly.
Note: Actual download tests are mocked to avoid network calls.
"""

import pytest
from unittest.mock import Mock, patch

from binance_data_downloader.downloaders import (
    KlineDownloader,
    TradeDownloader,
    AggTradeDownloader,
    FundingRateDownloader,
)


class TestKlineDownloader:
    """Test KlineDownloader."""

    def test_initialization_spot(self):
        """Test initializing downloader for spot market."""
        downloader = KlineDownloader(trading_type='spot')
        assert downloader.trading_type == 'spot'
        assert downloader.data_type == 'klines'

    def test_initialization_um(self):
        """Test initializing downloader for USD-M futures."""
        downloader = KlineDownloader(trading_type='um')
        assert downloader.trading_type == 'um'

    def test_supports_intervals(self):
        """Test that klines support intervals."""
        downloader = KlineDownloader(trading_type='spot')
        assert downloader.supports_intervals() is True

    def test_format_monthly_filename(self):
        """Test monthly filename formatting."""
        downloader = KlineDownloader(trading_type='spot')
        filename = downloader.format_monthly_filename('btcusdt', '1h', '2023', 6)
        assert filename == 'BTCUSDT-1h-2023-06.zip'

    def test_format_daily_filename(self):
        """Test daily filename formatting."""
        downloader = KlineDownloader(trading_type='spot')
        filename = downloader.format_daily_filename('btcusdt', '1h', '2023-06-15')
        assert filename == 'BTCUSDT-1h-2023-06-15.zip'


class TestTradeDownloader:
    """Test TradeDownloader."""

    def test_initialization(self):
        """Test initializing trade downloader."""
        downloader = TradeDownloader(trading_type='spot')
        assert downloader.data_type == 'trades'

    def test_does_not_support_intervals(self):
        """Test that trades don't support intervals."""
        downloader = TradeDownloader(trading_type='spot')
        assert downloader.supports_intervals() is False

    def test_format_monthly_filename(self):
        """Test monthly filename formatting."""
        downloader = TradeDownloader(trading_type='spot')
        filename = downloader.format_monthly_filename('btcusdt', None, '2023', 6)
        assert filename == 'BTCUSDT-trades-2023-06.zip'


class TestAggTradeDownloader:
    """Test AggTradeDownloader."""

    def test_initialization(self):
        """Test initializing agg trade downloader."""
        downloader = AggTradeDownloader(trading_type='spot')
        assert downloader.data_type == 'aggTrades'

    def test_format_monthly_filename(self):
        """Test monthly filename formatting."""
        downloader = AggTradeDownloader(trading_type='spot')
        filename = downloader.format_monthly_filename('ethusdt', None, '2024', 1)
        assert filename == 'ETHUSDT-aggTrades-2024-01.zip'


class TestFundingRateDownloader:
    """Test FundingRateDownloader."""

    def test_initialization_um(self):
        """Test initializing for USD-M futures."""
        downloader = FundingRateDownloader(trading_type='um')
        assert downloader.data_type == 'fundingRate'

    def test_initialization_cm(self):
        """Test initializing for COIN-M futures."""
        downloader = FundingRateDownloader(trading_type='cm')
        assert downloader.data_type == 'fundingRate'

    def test_spot_not_supported(self):
        """Test that funding rate is not available for spot."""
        with pytest.raises(ValueError, match="not supported"):
            FundingRateDownloader(trading_type='spot')

    def test_format_monthly_filename(self):
        """Test monthly filename formatting."""
        downloader = FundingRateDownloader(trading_type='um')
        filename = downloader.format_monthly_filename('btcusdt', None, '2023', 6)
        assert filename == 'BTCUSDT-fundingRate-2023-06.zip'


class TestFetcherSymbols:
    """Test symbol fetching from exchange."""

    @patch('binance_data_downloader.utils.file_operations.urllib.request.urlopen')
    def test_fetch_symbols_spot(self, mock_urlopen):
        """Test fetching spot symbols."""
        # Mock API response
        mock_response = Mock()
        mock_response.read.return_value = b'{"symbols": [{"symbol": "BTCUSDT"}, {"symbol": "ETHUSDT"}]}'
        mock_urlopen.return_value = mock_response

        symbols = KlineDownloader.fetch_symbols('spot')
        assert 'BTCUSDT' in symbols
        assert 'ETHUSDT' in symbols

    @patch('binance_data_downloader.utils.file_operations.urllib.request.urlopen')
    def test_fetch_symbols_um(self, mock_urlopen):
        """Test fetching USD-M futures symbols."""
        mock_response = Mock()
        mock_response.read.return_value = b'{"symbols": [{"symbol": "BTCUSDT"}, {"symbol": "ETHUSDT"}]}'
        mock_urlopen.return_value = mock_response

        symbols = KlineDownloader.fetch_symbols('um')
        assert len(symbols) > 0
