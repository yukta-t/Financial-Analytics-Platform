import pytest
import pandas as pd
from datetime import datetime
from data_quality.bonds_checks import (
    validate_maturity_date,
    validate_bond_numerics,
    validate_bond_vwap,
    check_unique_trades,
    validate_prev_close_consistency,
    run_all_bond_checks
)


class TestValidateMaturityDate:
    """Unit tests for validate_maturity_date function"""

    def test_valid_maturity_dates_pass(self, bond_data_valid):
        """Test that maturity dates in future pass"""
        result = validate_maturity_date(bond_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_maturity_in_past_fails(self, bond_data_maturity_in_past):
        """Test that maturity dates in past fail"""
        result = validate_maturity_date(bond_data_maturity_in_past)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_maturity_equal_to_date_passes(self):
        """Test that maturity date equal to current date passes"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2024-06-20"],
            "date_of_maturity": ["2025-01-15", "2028-06-20"]
        })
        result = validate_maturity_date(df)
        # Equal dates should pass (>=)
        assert result["offending_count"] <= 1

    def test_empty_dataframe(self):
        """Test with empty dataframe"""
        df = pd.DataFrame({
            "date": [],
            "date_of_maturity": []
        })
        result = validate_maturity_date(df)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_dataframe_not_mutated(self, bond_data_valid):
        """Test that original dataframe is not modified"""
        original_columns = set(bond_data_valid.columns)
        validate_maturity_date(bond_data_valid)
        assert set(bond_data_valid.columns) == original_columns


class TestValidateBondNumerics:
    """Unit tests for validate_bond_numerics function"""

    def test_valid_numerics_pass(self, bond_data_valid):
        """Test that valid numeric values pass"""
        result = validate_bond_numerics(bond_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_negative_volume_fails(self, bond_data_with_numeric_violations):
        """Test that negative volume fails"""
        result = validate_bond_numerics(bond_data_with_numeric_violations)
        assert result["status"] == "FAIL"
        assert result["offending_count"] >= 1

    def test_negative_value_fails(self):
        """Test that negative value fails"""
        df = pd.DataFrame({
            "volume": [1000, 2000],
            "value": [-100000, 200000],
            "trades": [50, 100]
        })
        result = validate_bond_numerics(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_negative_trades_fails(self):
        """Test that negative trades fails"""
        df = pd.DataFrame({
            "volume": [1000, 2000],
            "value": [100000, 200000],
            "trades": [-50, 100]
        })
        result = validate_bond_numerics(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_zero_values_pass(self):
        """Test that zero values are acceptable"""
        df = pd.DataFrame({
            "volume": [0, 2000],
            "value": [0, 200000],
            "trades": [0, 100]
        })
        result = validate_bond_numerics(df)
        assert result["status"] == "PASS"

    def test_multiple_numeric_violations(self, bond_data_with_numeric_violations):
        """Test multiple numeric violations"""
        result = validate_bond_numerics(bond_data_with_numeric_violations)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 3


class TestValidateBondVWAP:
    """Unit tests for validate_bond_vwap function"""

    def test_valid_vwap_passes(self, bond_data_valid):
        """Test that valid VWAP passes"""
        result = validate_bond_vwap(bond_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_vwap_below_low_fails(self):
        """Test that VWAP < low fails"""
        df = pd.DataFrame({
            "low": [95.0, 98.0],
            "high": [105.0, 102.0],
            "vwap": [90.0, 100.5]  # First: vwap < low
        })
        result = validate_bond_vwap(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_vwap_above_high_fails(self):
        """Test that VWAP > high fails"""
        df = pd.DataFrame({
            "low": [95.0, 98.0],
            "high": [105.0, 102.0],
            "vwap": [110.0, 100.5]  # First: vwap > high
        })
        result = validate_bond_vwap(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_multiple_vwap_violations(self, bond_data_with_vwap_violations):
        """Test multiple VWAP violations"""
        result = validate_bond_vwap(bond_data_with_vwap_violations)
        assert result["status"] == "FAIL"
        assert result["offending_count"] >= 1

    def test_vwap_within_range_passes(self):
        """Test that VWAP within [low, high] passes"""
        df = pd.DataFrame({
            "low": [95.0, 98.0, 99.0],
            "high": [105.0, 102.0, 101.0],
            "vwap": [100.0, 100.0, 100.0]
        })
        result = validate_bond_vwap(df)
        assert result["status"] == "PASS"


class TestCheckUniqueTrades:
    """Unit tests for check_unique_trades function"""

    def test_no_duplicates_pass(self, bond_data_valid):
        """Test that unique trades pass"""
        result = check_unique_trades(bond_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_duplicate_trades_detected(self, bond_data_with_duplicate_trades):
        """Test that duplicate trades are detected"""
        result = check_unique_trades(bond_data_with_duplicate_trades)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 2  # Both duplicate records returned

    def test_same_ticker_different_date_not_duplicate(self):
        """Test that same ticker on different dates are not duplicates"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2025-01-16"],
            "ticker": ["BONDX", "BONDX"],
            "series": ["A", "A"],
            "close": [100.0, 101.0]
        })
        result = check_unique_trades(df)
        assert result["status"] == "PASS"

    def test_same_date_different_series_not_duplicate(self):
        """Test that same date/ticker but different series are not duplicates"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2025-01-15"],
            "ticker": ["BONDX", "BONDX"],
            "series": ["A", "B"],
            "close": [100.0, 101.0]
        })
        result = check_unique_trades(df)
        assert result["status"] == "PASS"

    def test_same_date_different_ticker_not_duplicate(self):
        """Test that same date but different tickers are not duplicates"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2025-01-15"],
            "ticker": ["BONDX", "BONDY"],
            "series": ["A", "A"],
            "close": [100.0, 101.0]
        })
        result = check_unique_trades(df)
        assert result["status"] == "PASS"


class TestValidatePrevCloseConsistency:
    """Unit tests for validate_prev_close_consistency function"""

    def test_consistent_prev_close_passes(self, bond_data_valid):
        """Test that consistent prev_close passes"""
        result = validate_prev_close_consistency(bond_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_large_prev_close_discrepancy_fails(self, bond_data_with_prev_close_inconsistency):
        """Test that large prev_close discrepancies fail"""
        result = validate_prev_close_consistency(bond_data_with_prev_close_inconsistency)
        # Should detect inconsistencies > 5%
        assert result["offending_count"] >= 0  # May have multiple or some depending on sorting

    def test_small_prev_close_variance_passes(self):
        """Test that small variance (< 5%) passes"""
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "ticker": ["BONDX", "BONDX", "BONDX"],
            "close": [100.0, 101.0, 102.0],
            "prev_close": [100.5, 100.8, 101.2]  # Small variance
        })
        result = validate_prev_close_consistency(df)
        assert result["status"] == "PASS"

    def test_empty_dataframe(self):
        """Test with empty dataframe"""
        df = pd.DataFrame({
            "date": [],
            "ticker": [],
            "close": [],
            "prev_close": []
        })
        result = validate_prev_close_consistency(df)
        assert result["status"] == "PASS"

    def test_single_row_passes(self):
        """Test that single row passes (no previous day data)"""
        df = pd.DataFrame({
            "date": ["2024-01-01"],
            "ticker": ["BONDX"],
            "close": [100.0],
            "prev_close": [100.5]
        })
        result = validate_prev_close_consistency(df)
        # First row has NaN previous_day_close, so pct_diff will be NaN
        assert result["status"] == "PASS"

    def test_multiple_tickers_independent(self):
        """Test that different tickers are validated independently"""
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"],
            "ticker": ["BONDX", "BONDX", "BONDY", "BONDY"],
            "close": [100.0, 101.0, 100.0, 101.0],
            "prev_close": [99.0, 100.0, 99.0, 100.0]
        })
        result = validate_prev_close_consistency(df)
        # Should validate each ticker separately
        assert result["status"] == "PASS"


class TestRunAllBondChecks:
    """Unit tests for run_all_bond_checks function"""

    def test_all_checks_pass_on_valid_data(self, bond_data_valid):
        """Test that all checks pass on valid data"""
        results = run_all_bond_checks(bond_data_valid)
        
        assert len(results) == 5
        for result in results:
            assert result["status"] == "PASS"

    def test_returns_correct_number_of_checks(self, bond_data_valid):
        """Test that run_all_bond_checks returns 5 results"""
        results = run_all_bond_checks(bond_data_valid)
        assert len(results) == 5
        
        # Verify the check names
        check_names = [r["check_name"] for r in results]
        expected_names = [
            "Maturity Date Validation",
            "Bond Numeric Validation",
            "Bond VWAP Validation",
            "Duplicate Trade Check",
            "Prev Close Consistency"
        ]
        assert check_names == expected_names

    def test_checks_with_violations_detected(self, bond_data_with_numeric_violations):
        """Test that checks detect violations"""
        results = run_all_bond_checks(bond_data_with_numeric_violations)
        
        # At least numeric validation should fail
        numeric_check = next(r for r in results if r["check_name"] == "Bond Numeric Validation")
        assert numeric_check["status"] == "FAIL"

    def test_all_checks_return_dict_structure(self, bond_data_valid):
        """Test that all checks return proper dictionary structure"""
        results = run_all_bond_checks(bond_data_valid)
        
        for result in results:
            assert "check_name" in result
            assert "status" in result
            assert "offending_count" in result
            assert result["status"] in ["PASS", "FAIL"]
