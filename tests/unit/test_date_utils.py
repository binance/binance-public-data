"""
Unit tests for date utilities.
"""

import pytest
from datetime import date

from binance_data_downloader.utils.date_utils import (
    convert_to_date_object,
    get_start_end_date_objects,
    get_default_start_date,
    get_default_end_date,
    generate_date_range,
    is_date_in_range,
    validate_date_format,
    parse_year_month,
)


class TestDateUtils:
    """Test date utility functions."""

    def test_convert_to_date_object(self):
        """Test converting string to date object."""
        result = convert_to_date_object('2023-06-15')
        assert result == date(2023, 6, 15)
        assert isinstance(result, date)

    def test_convert_invalid_date(self):
        """Test converting invalid date string."""
        with pytest.raises(ValueError):
            convert_to_date_object('invalid-date')

    def test_get_start_end_date_objects(self):
        """Test parsing date range string."""
        start, end = get_start_end_date_objects('2023-01-01 2023-12-31')
        assert start == date(2023, 1, 1)
        assert end == date(2023, 12, 31)

    def test_get_default_start_date(self):
        """Test getting default start date."""
        start = get_default_start_date()
        assert start.year == 2017  # First year in YEARS list
        assert start.month == 1
        assert start.day == 1

    def test_get_default_end_date(self):
        """Test getting default end date."""
        end = get_default_end_date()
        assert end <= date.today()

    def test_generate_date_range(self):
        """Test generating date range."""
        dates = generate_date_range(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 5)
        )
        assert len(dates) == 5
        assert dates[0] == '2023-01-01'
        assert dates[-1] == '2023-01-05'

    def test_is_date_in_range_within(self):
        """Test date within range."""
        assert is_date_in_range(
            '2023-06-15',
            date(2023, 1, 1),
            date(2023, 12, 31)
        ) is True

    def test_is_date_in_range_before(self):
        """Test date before range."""
        assert is_date_in_range(
            '2022-12-31',
            date(2023, 1, 1),
            date(2023, 12, 31)
        ) is False

    def test_is_date_in_range_after(self):
        """Test date after range."""
        assert is_date_in_range(
            '2024-01-01',
            date(2023, 1, 1),
            date(2023, 12, 31)
        ) is False

    def test_is_date_in_range_no_bounds(self):
        """Test date with no bounds (None)."""
        assert is_date_in_range('2023-06-15', None, None) is True
        assert is_date_in_range('2023-06-15', date(2023, 1, 1), None) is True
        assert is_date_in_range('2023-06-15', None, date(2023, 12, 31)) is True

    def test_validate_date_format_valid(self):
        """Test valid date format."""
        assert validate_date_format('2023-06-15') is True

    def test_validate_date_format_invalid(self):
        """Test invalid date formats."""
        assert validate_date_format('2023/06/15') is False
        assert validate_date_format('15-06-2023') is False
        assert validate_date_format('invalid') is False

    def test_parse_year_month(self):
        """Test parsing year and month."""
        result = parse_year_month('2023', 6)
        assert result == date(2023, 6, 1)
