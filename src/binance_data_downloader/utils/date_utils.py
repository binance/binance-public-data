"""
Date Utilities

This module provides date parsing and manipulation utilities for data downloads.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple


# Default period start date
PERIOD_START_DATE = '2020-01-01'

# Available years
YEARS = ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']

# Available months
MONTHS = list(range(1, 13))


def convert_to_date_object(date_str: str) -> date:
    """
    Convert a date string to a date object.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        datetime.date object
    """
    year, month, day = [int(x) for x in date_str.split('-')]
    return date(year, month, day)


def get_start_end_date_objects(date_range: str) -> Tuple[date, date]:
    """
    Parse a date range string into start and end date objects.

    Args:
        date_range: Date range string with space-separated dates
                    (e.g., "2023-01-01 2023-12-31")

    Returns:
        Tuple of (start_date, end_date) as datetime.date objects
    """
    start, end = date_range.split()
    start_date = convert_to_date_object(start)
    end_date = convert_to_date_object(end)
    return start_date, end_date


def get_default_start_date() -> date:
    """Get the default start date (earliest year)."""
    return date(int(YEARS[0]), MONTHS[0], 1)


def get_default_end_date() -> date:
    """Get the default end date (today)."""
    return datetime.now().date()


def generate_date_range(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[str]:
    """
    Generate a list of date strings between start and end dates.

    Args:
        start_date: Start date (defaults to PERIOD_START_DATE)
        end_date: End date (defaults to today)

    Returns:
        List of date strings in YYYY-MM-DD format
    """
    if start_date is None:
        start_date = convert_to_date_object(PERIOD_START_DATE)
    if end_date is None:
        end_date = datetime.now().date()

    period = end_date - start_date
    dates = [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(period.days + 1)
    ]
    return dates


def filter_dates_by_range(
    dates: List[str],
    start_date: Optional[date],
    end_date: Optional[date]
) -> List[str]:
    """
    Filter a list of date strings by a date range.

    Args:
        dates: List of date strings in YYYY-MM-DD format
        start_date: Start date (inclusive), None for no lower bound
        end_date: End date (inclusive), None for no upper bound

    Returns:
        Filtered list of date strings
    """
    filtered = []
    for date_str in dates:
        current_date = convert_to_date_object(date_str)
        if start_date and current_date < start_date:
            continue
        if end_date and current_date > end_date:
            continue
        filtered.append(date_str)
    return filtered


def is_date_in_range(
    date_str: str,
    start_date: Optional[date],
    end_date: Optional[date]
) -> bool:
    """
    Check if a date is within the specified range.

    Args:
        date_str: Date string in YYYY-MM-DD format
        start_date: Start date (inclusive), None for no lower bound
        end_date: End date (inclusive), None for no upper bound

    Returns:
        True if date is within range, False otherwise
    """
    current_date = convert_to_date_object(date_str)
    if start_date and current_date < start_date:
        return False
    if end_date and current_date > end_date:
        return False
    return True


def validate_date_format(date_str: str) -> bool:
    """
    Validate that a string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate

    Returns:
        True if valid format, False otherwise
    """
    try:
        convert_to_date_object(date_str)
        return True
    except (ValueError, AttributeError):
        return False


def parse_year_month(year: str, month: int) -> date:
    """
    Create a date object from year and month.

    Args:
        year: Year as string
        month: Month (1-12)

    Returns:
        datetime.date object for the first day of the month
    """
    return date(int(year), month, 1)


def get_date_range_string(start_date: Optional[str], end_date: Optional[str]) -> Optional[str]:
    """
    Create a date range string from start and end dates.

    Args:
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format

    Returns:
        Date range string with dates separated by space, or None if either is None
    """
    if start_date and end_date:
        return f"{start_date} {end_date}"
    return None
