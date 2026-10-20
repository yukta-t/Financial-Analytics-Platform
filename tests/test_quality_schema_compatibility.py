"""Regression coverage for the supplied Snowflake quality-check schemas."""

import pandas as pd
import pytest

from data_quality.bonds_checks import (
    run_all_bond_checks,
    validate_prev_close_consistency,
)
from data_quality.security_master_checks import (
    check_duplicate_name_isin,
    run_all_security_master_checks,
)


@pytest.fixture
def snowflake_bonds():
    return pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "ticker": ["BOND1", "BOND1"],
        "series": ["A", "A"],
        "price": [100, 101],
        "face_value": [100, 100],
        "coupon_rate": [5, 5],
        "years_to_maturity": [5, 5],
        "date_of_maturity": ["2030-01-01", "2030-01-01"],
        "volume": [100, -1],
        "value": [10000, 10100],
        "trades": [1, 1],
        "vwap": [100, 101],
        "high": [102, 102],
        "low": [99, 99],
    })


@pytest.fixture
def snowflake_security_master():
    return pd.DataFrame({
        "ssm_id": ["SM1", "SM1"],
        "isin": ["ISIN1", "ISIN1"],
        "issuer_country": ["US", "US"],
        "currency_issue": ["USD", "USD"],
        "price": [100, -1],
        "security_sector": ["Finance", "Finance"],
        "duration": [1, 1],
        "convexity": [10, 10],
        "issuer_id": ["ISS1", "ISS1"],
        "related_ssm_id": [None, None],
    })


def assert_not_applicable(result, check_name, missing_columns):
    assert set(result) == {
        "check_name", "status", "offending_count", "sample_rows"
    }
    assert result["check_name"] == (
        f"{check_name} (NOT APPLICABLE: missing {', '.join(missing_columns)})"
    )
    assert result["status"] == "PASS"
    assert result["offending_count"] == 0
    assert result["sample_rows"] == []


@pytest.mark.parametrize(
    "missing_columns",
    [("close",), ("prev_close",), ("close", "prev_close")],
)
def test_previous_close_skips_if_either_required_price_is_absent(
    snowflake_bonds, missing_columns
):
    frame = snowflake_bonds.assign(
        close=[100, 101], prev_close=[99, 100]
    ).drop(columns=list(missing_columns))
    original = frame.copy(deep=True)

    result = validate_prev_close_consistency(frame)

    assert_not_applicable(result, "Prev Close Consistency", missing_columns)
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize(
    "missing_columns",
    [("name",), ("isin",), ("name", "isin")],
)
def test_duplicate_name_isin_skips_if_either_key_is_absent(
    snowflake_security_master, missing_columns
):
    frame = snowflake_security_master.assign(
        name=["Bond One", "Bond One"]
    ).drop(columns=list(missing_columns))
    original = frame.copy(deep=True)

    result = check_duplicate_name_isin(frame)

    assert_not_applicable(result, "Duplicate Name ISIN Check", missing_columns)
    pd.testing.assert_frame_equal(frame, original)


def test_bond_runner_keeps_all_checks_with_actual_schema(snowflake_bonds):
    results = run_all_bond_checks(snowflake_bonds)

    assert len(results) == 5
    assert results[1]["check_name"] == "Bond Numeric Validation"
    assert results[1]["status"] == "FAIL"
    assert results[1]["offending_count"] == 1
    assert_not_applicable(
        results[4], "Prev Close Consistency", ("close", "prev_close")
    )


def test_security_master_runner_keeps_all_checks_with_actual_schema(
    snowflake_security_master,
):
    results = run_all_security_master_checks(snowflake_security_master)

    assert len(results) == 3
    assert results[0]["status"] == "FAIL"
    assert results[0]["offending_count"] == 1
    assert results[1]["status"] == "FAIL"
    assert results[1]["offending_count"] == 2
    assert_not_applicable(results[2], "Duplicate Name ISIN Check", ("name",))


@pytest.mark.parametrize(
    ("datatype", "fixture_name", "skipped_name"),
    [
        (
            "bonds",
            "snowflake_bonds",
            "Prev Close Consistency (NOT APPLICABLE: missing close, prev_close)",
        ),
        (
            "security_master",
            "snowflake_security_master",
            "Duplicate Name ISIN Check (NOT APPLICABLE: missing name)",
        ),
    ],
)
def test_quality_api_preserves_response_shape_with_actual_schemas(
    client, auth_token, monkeypatch, request, datatype, fixture_name, skipped_name
):
    frame = request.getfixturevalue(fixture_name)
    monkeypatch.setattr("app.load_table", lambda selected: frame)

    response = client.get(
        "/api/quality",
        query_string={"datatype": datatype},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert set(body) == {"status", "checks"}
    assert body["status"] == "ok"
    assert len(body["checks"]) == 5
    for check in body["checks"]:
        assert set(check) == {
            "check_name", "status", "offending_count", "sample_rows"
        }
    skipped = next(
        check for check in body["checks"] if check["check_name"] == skipped_name
    )
    assert skipped["status"] == "PASS"
    assert skipped["offending_count"] == 0
    assert skipped["sample_rows"] == []
