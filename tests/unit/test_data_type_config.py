"""
Unit tests for data type configuration.
"""

import pytest

from binance_data_downloader.core.data_type_config import (
    DataType,
    get_data_type_spec,
    get_supported_data_types,
    get_all_data_types,
    is_interval_supported,
    get_path_segment,
)


class TestDataType:
    """Test DataType enum and related functions."""

    def test_all_data_types_defined(self):
        """Verify all expected data types are defined."""
        expected_types = {
            'klines', 'trades', 'aggTrades',
            'indexPriceKlines', 'markPriceKlines', 'premiumIndexKlines',
            'fundingRate', 'liquidationSnapshot', 'bookTicker', 'depth', 'option'
        }
        actual_types = {dt.value for dt in DataType}
        assert actual_types == expected_types

    def test_get_data_type_spec(self):
        """Test getting specifications for each data type."""
        for dt in DataType:
            spec = get_data_type_spec(dt)
            assert spec is not None
            assert spec.data_type == dt
            assert spec.path_segment
            assert isinstance(spec.supports_spot, bool)
            assert isinstance(spec.supports_um, bool)
            assert isinstance(spec.supports_cm, bool)

    def test_klines_spec(self):
        """Test klines data type specification."""
        spec = get_data_type_spec(DataType.KLINES)
        assert spec.path_segment == "klines"
        assert spec.supports_spot is True
        assert spec.supports_um is True
        assert spec.supports_cm is True
        assert spec.supports_intervals is True
        assert spec.supports_monthly is True
        assert spec.supports_daily is True

    def test_trades_spec(self):
        """Test trades data type specification."""
        spec = get_data_type_spec(DataType.TRADES)
        assert spec.path_segment == "trades"
        assert spec.supports_intervals is False

    def test_premium_index_spec(self):
        """Test premium index klines specification."""
        spec = get_data_type_spec(DataType.PREMIUM_INDEX_KLINES)
        assert spec.supports_spot is False
        assert spec.supports_um is True
        assert spec.supports_cm is False

    def test_get_supported_data_types_spot(self):
        """Test getting supported data types for spot market."""
        types = get_supported_data_types('spot')
        assert DataType.KLINES in types
        assert DataType.TRADES in types
        assert DataType.AGG_TRADES in types
        assert DataType.FUNDING_RATE not in types

    def test_get_supported_data_types_um(self):
        """Test getting supported data types for USD-M futures."""
        types = get_supported_data_types('um')
        assert DataType.KLINES in types
        assert DataType.FUNDING_RATE in types
        assert DataType.PREMIUM_INDEX_KLINES in types
        assert DataType.LIQUIDATION_SNAPSHOT not in types

    def test_get_supported_data_types_cm(self):
        """Test getting supported data types for COIN-M futures."""
        types = get_supported_data_types('cm')
        assert DataType.KLINES in types
        assert DataType.FUNDING_RATE in types
        assert DataType.LIQUIDATION_SNAPSHOT in types
        assert DataType.PREMIUM_INDEX_KLINES not in types

    def test_get_all_data_types(self):
        """Test getting all data types."""
        types = get_all_data_types()
        assert len(types) == 11
        assert DataType.KLINES in types
        assert DataType.OPTION in types

    def test_is_interval_supported(self):
        """Test interval support checking."""
        assert is_interval_supported(DataType.KLINES) is True
        assert is_interval_supported(DataType.TRADES) is False
        assert is_interval_supported(DataType.FUNDING_RATE) is False

    def test_get_path_segment(self):
        """Test getting path segments."""
        assert get_path_segment(DataType.KLINES) == "klines"
        assert get_path_segment(DataType.TRADES) == "trades"
        assert get_path_segment(DataType.FUNDING_RATE) == "fundingRate"
