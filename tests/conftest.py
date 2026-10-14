"""Shared test fixtures for quality check tests"""
import os
import sys
import pytest
import pandas as pd
from datetime import datetime, timedelta

# backend/app.py uses flat (non-package) imports internally (e.g. `from auth
# import ...`), so `backend/` must be on sys.path for it to import cleanly.
# `backend` is inserted ahead of the project root so `import app` resolves to
# backend/app.py rather than the empty root-level app.py.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_PROJECT_ROOT, "backend")

if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(1, _PROJECT_ROOT)

from app import app as _flask_app  # noqa: E402  (backend/app.py's Flask instance)


@pytest.fixture
def app():
    """The Flask app under test, configured for testing with an active app context."""
    _flask_app.config.update(TESTING=True)
    with _flask_app.app_context():
        yield _flask_app


@pytest.fixture
def client(app):
    """Flask test client bound to the `app` fixture."""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """A valid JWT access token obtained via /api/login."""
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "admin123"},
    )
    return response.get_json()["access_token"]


@pytest.fixture
def stock_data_valid():
    """Sample valid stock data"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["INFY", "TCS", "RELIANCE"],
        "open": [1500, 3000, 2500],
        "high": [1550, 3100, 2550],
        "low": [1450, 2950, 2450],
        "close": [1525, 3050, 2520],
        "volume": [1000000, 2000000, 1500000],
        "vwap": [1520, 3010, 2500]
    })


@pytest.fixture
def stock_data_with_price_violations():
    """Stock data with price range violations"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["INFY", "TCS", "RELIANCE"],
        "open": [1500, 2000, 2500],  # TCS open < low
        "high": [1550, 3100, 2550],
        "low": [1450, 2950, 2450],
        "close": [1525, 3050, -100],  # RELIANCE close is negative
        "volume": [1000000, 2000000, 1500000],
        "vwap": [1520, 3010, 2500]
    })


@pytest.fixture
def stock_data_with_duplicates():
    """Stock data with duplicate records"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2025-01-15", "2023-12-01"],
        "ticker": ["INFY", "INFY", "RELIANCE"],
        "open": [1500, 1500, 2500],
        "high": [1550, 1550, 2550],
        "low": [1450, 1450, 2450],
        "close": [1525, 1525, 2520],
        "volume": [1000000, 1000000, 1500000],
        "vwap": [1520, 1520, 2500]
    })


@pytest.fixture
def stock_data_with_vwap_violations():
    """Stock data with VWAP violations"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["INFY", "TCS", "RELIANCE"],
        "open": [1500, 3000, 2500],
        "high": [1550, 3100, 2550],
        "low": [1450, 2950, 2450],
        "close": [1525, 3050, 2520],
        "volume": [1000000, 2000000, 1500000],
        "vwap": [1600, 2900, 2500]  # INFY VWAP > high, TCS VWAP < low
    })


@pytest.fixture
def bond_data_valid():
    """Sample valid bond data"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["BONDX", "BONDY", "BONDZ"],
        "series": ["A", "B", "C"],
        "low": [95.0, 98.0, 97.0],
        "high": [105.0, 102.0, 103.0],
        "vwap": [100.0, 100.5, 100.0],
        "volume": [1000, 2000, 1500],
        "value": [100000, 200000, 150000],
        "trades": [50, 100, 75],
        "prev_close": [100.5, 100.2, 99.8],
        "close": [100.0, 100.5, 100.0],
        "date_of_maturity": ["2030-01-15", "2028-06-20", "2026-12-01"]
    })


@pytest.fixture
def bond_data_with_numeric_violations():
    """Bond data with numeric violations"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["BONDX", "BONDY", "BONDZ"],
        "series": ["A", "B", "C"],
        "low": [95.0, 98.0, 97.0],
        "high": [105.0, 102.0, 103.0],
        "vwap": [100.0, 100.5, 100.0],
        "volume": [-1000, 2000, 1500],  # Negative volume
        "value": [100000, -200000, 150000],  # Negative value
        "trades": [50, 100, -75],  # Negative trades
        "prev_close": [100.5, 100.2, 99.8],
        "close": [100.0, 100.5, 100.0],
        "date_of_maturity": ["2030-01-15", "2028-06-20", "2026-12-01"]
    })


@pytest.fixture
def bond_data_with_vwap_violations():
    """Bond data with VWAP violations"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["BONDX", "BONDY", "BONDZ"],
        "series": ["A", "B", "C"],
        "low": [95.0, 98.0, 97.0],
        "high": [105.0, 102.0, 103.0],
        "vwap": [106.0, 97.0, 100.0],  # VWAP violations
        "volume": [1000, 2000, 1500],
        "value": [100000, 200000, 150000],
        "trades": [50, 100, 75],
        "prev_close": [100.5, 100.2, 99.8],
        "close": [100.0, 100.5, 100.0],
        "date_of_maturity": ["2030-01-15", "2028-06-20", "2026-12-01"]
    })


@pytest.fixture
def bond_data_with_duplicate_trades():
    """Bond data with duplicate trades"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2025-01-15", "2023-12-01"],
        "ticker": ["BONDX", "BONDX", "BONDZ"],
        "series": ["A", "A", "C"],
        "low": [95.0, 95.0, 97.0],
        "high": [105.0, 105.0, 103.0],
        "vwap": [100.0, 100.0, 100.0],
        "volume": [1000, 1000, 1500],
        "value": [100000, 100000, 150000],
        "trades": [50, 50, 75],
        "prev_close": [100.5, 100.5, 99.8],
        "close": [100.0, 100.0, 100.0],
        "date_of_maturity": ["2030-01-15", "2030-01-15", "2026-12-01"]
    })


@pytest.fixture
def bond_data_with_prev_close_inconsistency():
    """Bond data with prev_close inconsistencies"""
    return pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "ticker": ["BONDX", "BONDX", "BONDX"],
        "close": [100.0, 101.0, 102.0],
        "prev_close": [100.5, 80.0, 105.0],  # Large discrepancies
        "low": [95.0, 98.0, 97.0],
        "high": [105.0, 102.0, 103.0],
        "vwap": [100.0, 100.5, 100.0],
        "volume": [1000, 2000, 1500],
        "value": [100000, 200000, 150000],
        "trades": [50, 100, 75],
        "series": ["A", "A", "A"],
        "date_of_maturity": ["2030-01-01", "2030-01-02", "2030-01-03"]
    })


@pytest.fixture
def bond_data_maturity_in_past():
    """Bond data with maturity dates in the past"""
    return pd.DataFrame({
        "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
        "ticker": ["BONDX", "BONDY", "BONDZ"],
        "date_of_maturity": ["2020-01-15", "2028-06-20", "2026-12-01"],  # First one is in past
        "low": [95.0, 98.0, 97.0],
        "high": [105.0, 102.0, 103.0],
        "vwap": [100.0, 100.5, 100.0],
        "volume": [1000, 2000, 1500],
        "value": [100000, 200000, 150000],
        "trades": [50, 100, 75],
        "prev_close": [100.5, 100.2, 99.8],
        "close": [100.0, 100.5, 100.0],
        "series": ["A", "B", "C"]
    })


@pytest.fixture
def security_master_data_valid():
    """Sample valid security master data"""
    return pd.DataFrame({
        "ssm_id": ["SM001", "SM002", "SM003"],
        "name": ["Bond X", "Bond Y", "Bond Z"],
        "isin": ["ISIN001", "ISIN002", "ISIN003"],
        "issuer_country": ["IN", "IN", "IN"],
        "price": [100.0, 95.5, 102.3],
        "duration": [5.0, 3.5, 7.2],
        "convexity": [50.0, 30.0, 60.0]
    })


@pytest.fixture
def security_master_data_numeric_violations():
    """Security master data with numeric violations"""
    return pd.DataFrame({
        "ssm_id": ["SM001", "SM002", "SM003"],
        "name": ["Bond X", "Bond Y", "Bond Z"],
        "isin": ["ISIN001", "ISIN002", "ISIN003"],
        "issuer_country": ["IN", "IN", "IN"],
        "price": [0, 95.5, 150000],  # Price <= 0 and > 100000
        "duration": [-1.0, 3.5, 7.2],  # Negative duration
        "convexity": [50.0, 1001.0, 60.0]  # Convexity > 1000
    })


@pytest.fixture
def security_master_data_duplicate_ssm_id():
    """Security master data with duplicate SSM_IDs"""
    return pd.DataFrame({
        "ssm_id": ["SM001", "SM001", "SM003"],
        "name": ["Bond X", "Bond X", "Bond Z"],
        "isin": ["ISIN001", "ISIN001", "ISIN003"],
        "issuer_country": ["IN", "IN", "IN"],
        "price": [100.0, 100.0, 102.3],
        "duration": [5.0, 5.0, 7.2],
        "convexity": [50.0, 50.0, 60.0]
    })


@pytest.fixture
def security_master_data_duplicate_name_isin():
    """Security master data with duplicate Name-ISIN pairs"""
    return pd.DataFrame({
        "ssm_id": ["SM001", "SM002", "SM003"],
        "name": ["Bond X", "Bond X", "Bond Z"],
        "isin": ["ISIN001", "ISIN001", "ISIN003"],
        "issuer_country": ["IN", "IN", "IN"],
        "price": [100.0, 101.0, 102.3],
        "duration": [5.0, 5.1, 7.2],
        "convexity": [50.0, 50.5, 60.0]
    })


@pytest.fixture
def security_master_data_missing_values():
    """Security master data with missing values"""
    return pd.DataFrame({
        "ssm_id": ["SM001", "SM002", None],
        "name": ["Bond X", None, "Bond Z"],
        "isin": ["ISIN001", "ISIN002", None],
        "issuer_country": ["IN", None, "IN"],
        "price": [100.0, 95.5, 102.3],
        "duration": [5.0, 3.5, 7.2],
        "convexity": [50.0, 30.0, 60.0]
    })
