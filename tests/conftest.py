"""
Pytest configuration and fixtures for Binance data downloader tests.
"""

import os
import sys
import tempfile
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_symbols():
    """Sample trading symbols for testing."""
    return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']


@pytest.fixture
def sample_intervals():
    """Sample kline intervals for testing."""
    return ['1m', '1h', '1d']


@pytest.fixture
def sample_years():
    """Sample years for testing."""
    return ['2023', '2024']


@pytest.fixture
def sample_months():
    """Sample months for testing."""
    return [1, 6, 12]


@pytest.fixture
def sample_dates():
    """Sample dates for testing."""
    return ['2023-01-01', '2023-01-15', '2023-12-31']
