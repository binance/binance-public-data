"""
Data Type Configuration Registry

This module defines all supported data types for Binance public data downloaders.
It provides a centralized registry of data type specifications including market support,
path components, and file naming patterns.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set


class DataType(Enum):
    """Enumeration of all supported Binance data types."""
    KLINES = "klines"
    TRADES = "trades"
    AGG_TRADES = "aggTrades"
    INDEX_PRICE_KLINES = "indexPriceKlines"
    MARK_PRICE_KLINES = "markPriceKlines"
    PREMIUM_INDEX_KLINES = "premiumIndexKlines"
    FUNDING_RATE = "fundingRate"
    LIQUIDATION_SNAPSHOT = "liquidationSnapshot"
    BOOK_TICKER = "bookTicker"
    DEPTH = "depth"
    OPTION = "option"


@dataclass
class DataTypeSpec:
    """
    Specification for a data type.

    Attributes:
        data_type: The DataType enum value
        path_segment: URL path segment for this data type
        supports_spot: Whether this data type is available for spot market
        supports_um: Whether this data type is available for USD-M futures
        supports_cm: Whether this data type is available for COIN-M futures
        supports_intervals: Whether this data type supports interval parameter
        supports_monthly: Whether monthly files are available
        supports_daily: Whether daily files are available
        has_interval_in_path: Whether interval appears in file path
    """
    data_type: DataType
    path_segment: str
    supports_spot: bool
    supports_um: bool
    supports_cm: bool
    supports_intervals: bool
    supports_monthly: bool
    supports_daily: bool
    has_interval_in_path: bool


# Data Type Registry
# Maps each DataType to its specification
DATA_TYPE_REGISTRY: Dict[DataType, DataTypeSpec] = {
    DataType.KLINES: DataTypeSpec(
        data_type=DataType.KLINES,
        path_segment="klines",
        supports_spot=True,
        supports_um=True,
        supports_cm=True,
        supports_intervals=True,
        supports_monthly=True,
        supports_daily=True,
        has_interval_in_path=True
    ),
    DataType.TRADES: DataTypeSpec(
        data_type=DataType.TRADES,
        path_segment="trades",
        supports_spot=True,
        supports_um=True,
        supports_cm=True,
        supports_intervals=False,
        supports_monthly=True,
        supports_daily=True,
        has_interval_in_path=False
    ),
    DataType.AGG_TRADES: DataTypeSpec(
        data_type=DataType.AGG_TRADES,
        path_segment="aggTrades",
        supports_spot=True,
        supports_um=True,
        supports_cm=True,
        supports_intervals=False,
        supports_monthly=True,
        supports_daily=True,
        has_interval_in_path=False
    ),
    DataType.INDEX_PRICE_KLINES: DataTypeSpec(
        data_type=DataType.INDEX_PRICE_KLINES,
        path_segment="indexPriceKlines",
        supports_spot=False,
        supports_um=True,
        supports_cm=True,
        supports_intervals=True,
        supports_monthly=True,
        supports_daily=True,
        has_interval_in_path=True
    ),
    DataType.MARK_PRICE_KLINES: DataTypeSpec(
        data_type=DataType.MARK_PRICE_KLINES,
        path_segment="markPriceKlines",
        supports_spot=False,
        supports_um=True,
        supports_cm=True,
        supports_intervals=True,
        supports_monthly=True,
        supports_daily=True,
        has_interval_in_path=True
    ),
    DataType.PREMIUM_INDEX_KLINES: DataTypeSpec(
        data_type=DataType.PREMIUM_INDEX_KLINES,
        path_segment="premiumIndexKlines",
        supports_spot=False,
        supports_um=True,
        supports_cm=False,
        supports_intervals=True,
        supports_monthly=True,
        supports_daily=True,
        has_interval_in_path=True
    ),
    DataType.FUNDING_RATE: DataTypeSpec(
        data_type=DataType.FUNDING_RATE,
        path_segment="fundingRate",
        supports_spot=False,
        supports_um=True,
        supports_cm=True,
        supports_intervals=False,
        supports_monthly=True,
        supports_daily=False,  # Funding rate only has monthly data, not daily
        has_interval_in_path=False
    ),
    DataType.LIQUIDATION_SNAPSHOT: DataTypeSpec(
        data_type=DataType.LIQUIDATION_SNAPSHOT,
        path_segment="liquidationSnapshot",
        supports_spot=False,
        supports_um=False,
        supports_cm=True,
        supports_intervals=False,
        supports_monthly=False,
        supports_daily=True,
        has_interval_in_path=False
    ),
    DataType.BOOK_TICKER: DataTypeSpec(
        data_type=DataType.BOOK_TICKER,
        path_segment="bookTicker",
        supports_spot=False,
        supports_um=True,
        supports_cm=True,
        supports_intervals=False,
        supports_monthly=False,
        supports_daily=True,
        has_interval_in_path=False
    ),
    DataType.DEPTH: DataTypeSpec(
        data_type=DataType.DEPTH,
        path_segment="depth",
        supports_spot=True,
        supports_um=True,
        supports_cm=False,
        supports_intervals=False,
        supports_monthly=False,
        supports_daily=True,
        has_interval_in_path=False
    ),
    DataType.OPTION: DataTypeSpec(
        data_type=DataType.OPTION,
        path_segment="BVOLIndex",
        supports_spot=False,
        supports_um=False,
        supports_cm=False,
        supports_intervals=False,
        supports_monthly=False,
        supports_daily=True,
        has_interval_in_path=False
    ),
}


def get_data_type_spec(data_type: DataType) -> Optional[DataTypeSpec]:
    """
    Get the specification for a given data type.

    Args:
        data_type: The DataType enum value

    Returns:
        DataTypeSpec if found, None otherwise
    """
    return DATA_TYPE_REGISTRY.get(data_type)


def get_supported_data_types(market_type: str) -> List[DataType]:
    """
    Get all data types supported by a given market type.

    Args:
        market_type: Market type ('spot', 'um', or 'cm')

    Returns:
        List of DataType values supported by the market
    """
    supported = []
    for data_type, spec in DATA_TYPE_REGISTRY.items():
        if market_type == 'spot' and spec.supports_spot:
            supported.append(data_type)
        elif market_type == 'um' and spec.supports_um:
            supported.append(data_type)
        elif market_type == 'cm' and spec.supports_cm:
            supported.append(data_type)
    return supported


def get_all_data_types() -> List[DataType]:
    """Get all available data types."""
    return list(DataType)


def is_interval_supported(data_type: DataType) -> bool:
    """
    Check if a data type supports interval parameter.

    Args:
        data_type: The DataType to check

    Returns:
        True if intervals are supported, False otherwise
    """
    spec = get_data_type_spec(data_type)
    return spec.supports_intervals if spec else False


def get_path_segment(data_type: DataType) -> Optional[str]:
    """
    Get the URL path segment for a data type.

    Args:
        data_type: The DataType enum value

    Returns:
        Path segment string or None if not found
    """
    spec = get_data_type_spec(data_type)
    return spec.path_segment if spec else None
