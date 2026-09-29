import pytest
import pandas as pd
from datetime import datetime, timedelta
from data_quality.stock_checks import (
    validate_date_fields,
    validate_price_ranges,
    validate_volume,
    check_duplicate_records,
    validate_vwap,
    run_all_stock_checks
)


class TestValidateDateFields:
    """Unit tests for validate_date_fields function"""

    def test_valid_dates_pass(self):
        """Test that dataframe with valid past dates passes"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_invalid_date_format_fails(self):
        """Test that invalid date formats are caught"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "invalid-date", "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1
        assert result["sample_rows"][0]["date"] == "invalid-date"

    def test_future_dates_rejected(self):
        """Test that future dates are rejected"""
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        df = pd.DataFrame({
            "date": ["2025-01-15", tomorrow, "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_today_date_passes(self):
        """Test that today's date is accepted"""
        today = datetime.today().strftime("%Y-%m-%d")
        df = pd.DataFrame({
            "date": ["2025-01-15", today, "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_multiple_invalid_dates(self):
        """Test multiple validation failures together"""
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        df = pd.DataFrame({
            "date": ["2025-01-15", "invalid", tomorrow, "also-bad"],
            "stock_id": [1, 2, 3, 4]
        })
        result = validate_date_fields(df)
        
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 3

    def test_empty_dataframe(self):
        """Test with empty dataframe"""
        df = pd.DataFrame({"date": [], "stock_id": []})
        result = validate_date_fields(df)
        
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_null_dates_fail(self):
        """Test that NULL/NaN dates are caught"""
        df = pd.DataFrame({
            "date": ["2025-01-15", None, "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_various_date_formats(self):
        """Test that ISO format dates are parsed correctly"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2024-06-20", "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        # Standard ISO format should pass
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0
    
    def test_non_standard_date_format_fails(self):
        """Test that non-standard date formats are rejected if not parseable"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "15-Jan-2025", "invalid"],
            "stock_id": [1, 2, 3]
        })
        result = validate_date_fields(df)
        
        # Non-standard format "15-Jan-2025" will fail to parse
        assert result["status"] == "FAIL"
        assert result["offending_count"] >= 1

    def test_dataframe_not_mutated(self):
        """Test that original dataframe is not modified"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "invalid", "2023-12-01"],
            "stock_id": [1, 2, 3]
        })
        original_columns = set(df.columns)
        
        validate_date_fields(df)
        
        # Original dataframe should not have "parsed_date" column
        assert set(df.columns) == original_columns
        assert "parsed_date" not in df.columns


class TestValidatePriceRanges:
    """Unit tests for validate_price_ranges function"""

    def test_valid_price_ranges_pass(self, stock_data_valid):
        """Test that valid price ranges pass"""
        result = validate_price_ranges(stock_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_high_less_than_low_fails(self):
        """Test that high < low fails"""
        df = pd.DataFrame({
            "high": [1000, 3000, 2500],
            "low": [1500, 2950, 2450],  # First: high < low
            "open": [1200, 3000, 2500],  # All values that don't violate other conditions
            "close": [1450, 2950, 2450]  # All values that don't violate other conditions
        })
        result = validate_price_ranges(df)
        assert result["status"] == "FAIL"
        # First row violates high < low (and possibly open < low and close < low)
        # But we should have at least the first row as a violation
        assert result["offending_count"] >= 1

    def test_open_below_low_fails(self):
        """Test that open < low fails"""
        df = pd.DataFrame({
            "high": [1550, 3100, 2550],
            "low": [1450, 2950, 2450],
            "open": [1400, 3000, 2500],  # First: open < low
            "close": [1525, 3050, 2520]
        })
        result = validate_price_ranges(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_open_above_high_fails(self):
        """Test that open > high fails"""
        df = pd.DataFrame({
            "high": [1550, 3100, 2550],
            "low": [1450, 2950, 2450],
            "open": [1600, 3000, 2500],  # First: open > high
            "close": [1525, 3050, 2520]
        })
        result = validate_price_ranges(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_close_below_low_fails(self):
        """Test that close < low fails"""
        df = pd.DataFrame({
            "high": [1550, 3100, 2550],
            "low": [1450, 2950, 2450],
            "open": [1500, 3000, 2500],
            "close": [1400, 3050, 2520]  # First: close < low
        })
        result = validate_price_ranges(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_close_above_high_fails(self):
        """Test that close > high fails"""
        df = pd.DataFrame({
            "high": [1550, 3100, 2550],
            "low": [1450, 2950, 2450],
            "open": [1500, 3000, 2500],
            "close": [1600, 3050, 2520]  # First: close > high
        })
        result = validate_price_ranges(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_negative_close_fails(self):
        """Test that negative close fails"""
        df = pd.DataFrame({
            "high": [1550, 3100, 2550],
            "low": [1450, 2950, 2450],
            "open": [1500, 3000, 2500],
            "close": [1525, 3050, -100]  # Third: close < 0
        })
        result = validate_price_ranges(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_multiple_price_violations(self, stock_data_with_price_violations):
        """Test multiple price violations"""
        result = validate_price_ranges(stock_data_with_price_violations)
        assert result["status"] == "FAIL"
        assert result["offending_count"] >= 1


class TestValidateVolume:
    """Unit tests for validate_volume function"""

    def test_valid_volume_passes(self, stock_data_valid):
        """Test that valid volume passes"""
        result = validate_volume(stock_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_negative_volume_fails(self):
        """Test that negative volume fails"""
        df = pd.DataFrame({
            "volume": [1000000, -200000, 1500000]
        })
        result = validate_volume(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_null_volume_fails(self):
        """Test that null volume fails"""
        df = pd.DataFrame({
            "volume": [1000000, None, 1500000]
        })
        result = validate_volume(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_zero_volume_passes(self):
        """Test that zero volume is acceptable"""
        df = pd.DataFrame({
            "volume": [1000000, 0, 1500000]
        })
        result = validate_volume(df)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_multiple_volume_violations(self):
        """Test multiple volume violations"""
        df = pd.DataFrame({
            "volume": [-100, None, -200, 1000]
        })
        result = validate_volume(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 3


class TestCheckDuplicateRecords:
    """Unit tests for check_duplicate_records function"""

    def test_no_duplicates_pass(self, stock_data_valid):
        """Test that no duplicates pass"""
        result = check_duplicate_records(stock_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_duplicates_detected(self, stock_data_with_duplicates):
        """Test that duplicates are detected"""
        result = check_duplicate_records(stock_data_with_duplicates)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 2  # Both duplicate records returned

    def test_different_dates_not_duplicates(self):
        """Test that same ticker on different dates are not duplicates"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2025-01-16"],
            "ticker": ["INFY", "INFY"],
            "close": [1525, 1530]
        })
        result = check_duplicate_records(df)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_different_tickers_not_duplicates(self):
        """Test that different tickers on same date are not duplicates"""
        df = pd.DataFrame({
            "date": ["2025-01-15", "2025-01-15"],
            "ticker": ["INFY", "TCS"],
            "close": [1525, 3050]
        })
        result = check_duplicate_records(df)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0


class TestValidateVWAP:
    """Unit tests for validate_vwap function"""

    def test_valid_vwap_passes(self, stock_data_valid):
        """Test that valid VWAP passes"""
        result = validate_vwap(stock_data_valid)
        assert result["status"] == "PASS"
        assert result["offending_count"] == 0

    def test_vwap_below_low_fails(self):
        """Test that VWAP < low fails"""
        df = pd.DataFrame({
            "low": [1450, 2950, 2450],
            "high": [1550, 3100, 2550],
            "vwap": [1400, 3010, 2500]  # First: vwap < low
        })
        result = validate_vwap(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_vwap_above_high_fails(self):
        """Test that VWAP > high fails"""
        df = pd.DataFrame({
            "low": [1450, 2950, 2450],
            "high": [1550, 3100, 2550],
            "vwap": [1600, 3010, 2500]  # First: vwap > high
        })
        result = validate_vwap(df)
        assert result["status"] == "FAIL"
        assert result["offending_count"] == 1

    def test_multiple_vwap_violations(self, stock_data_with_vwap_violations):
        """Test multiple VWAP violations"""
        result = validate_vwap(stock_data_with_vwap_violations)
        assert result["status"] == "FAIL"
        assert result["offending_count"] >= 1

    def test_vwap_equal_to_low_passes(self):
        """Test that VWAP = low passes"""
        df = pd.DataFrame({
            "low": [1450, 2950, 2450],
            "high": [1550, 3100, 2550],
            "vwap": [1450, 3010, 2500]
        })
        result = validate_vwap(df)
        assert result["status"] == "PASS"

    def test_vwap_equal_to_high_passes(self):
        """Test that VWAP = high passes"""
        df = pd.DataFrame({
            "low": [1450, 2950, 2450],
            "high": [1550, 3100, 2550],
            "vwap": [1550, 3010, 2500]
        })
        result = validate_vwap(df)
        assert result["status"] == "PASS"


class TestRunAllStockChecks:
    """Unit tests for run_all_stock_checks function"""

    def test_all_checks_pass_on_valid_data(self, stock_data_valid):
        """Test that all checks pass on valid data"""
        results = run_all_stock_checks(stock_data_valid)
        
        assert len(results) == 5
        for result in results:
            assert result["status"] == "PASS"

    def test_returns_correct_number_of_checks(self, stock_data_valid):
        """Test that run_all_stock_checks returns 5 results"""
        results = run_all_stock_checks(stock_data_valid)
        assert len(results) == 5
        
        # Verify the check names
        check_names = [r["check_name"] for r in results]
        expected_names = [
            "Date Validity",
            "Price Sanity",
            "Volume Validation",
            "Duplicate Records",
            "VWAP Validation"
        ]
        assert check_names == expected_names

    def test_all_checks_with_violations(self, stock_data_with_price_violations):
        """Test that checks detect violations"""
        results = run_all_stock_checks(stock_data_with_price_violations)
        
        # At least price sanity should fail
        price_sanity = next(r for r in results if r["check_name"] == "Price Sanity")
        assert price_sanity["status"] == "FAIL"
