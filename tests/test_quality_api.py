"""Integration tests for the Data Quality Center API."""

import pandas as pd


def test_quality_requires_authentication(client):
    response = client.get(
        "/api/quality",
        query_string={"datatype": "stock"}
    )

    assert response.status_code == 401


def test_quality_rejects_invalid_datatype(client, auth_token):
    response = client.get(
        "/api/quality",
        query_string={"datatype": "unknown"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400


def test_quality_stock_returns_existing_checks_and_sample_rows(
    client,
    auth_token,
    monkeypatch,
    stock_data_with_duplicates
):
    stock_data = stock_data_with_duplicates.copy()
    stock_data.loc[:1, "date"] = "not-a-date"
    monkeypatch.setattr(
        "app.load_table",
        lambda datatype: stock_data
    )

    response = client.get(
        "/api/quality",
        query_string={"datatype": "stock"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    body = response.get_json()
    checks = {check["check_name"]: check for check in body["checks"]}
    assert body["status"] == "ok"
    assert len(checks) == 5
    assert checks["Duplicate Detection"]["status"] == "FAIL"
    assert checks["Duplicate Detection"]["offending_count"] == 2
    assert len(checks["Duplicate Detection"]["sample_rows"]) == 2
    assert checks["Date Validity"]["status"] == "FAIL"
    assert checks["Date Validity"]["sample_rows"][0]["parsed_date"] is None


def test_quality_bonds_returns_all_existing_checks(
    client,
    auth_token,
    monkeypatch,
    bond_data_valid
):
    monkeypatch.setattr(
        "app.load_table",
        lambda datatype: bond_data_valid
    )

    response = client.get(
        "/api/quality",
        query_string={"datatype": "bonds"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    checks = response.get_json()["checks"]
    assert [check["check_name"] for check in checks] == [
        "Maturity Validation",
        "Numeric Validation",
        "VWAP Validation",
        "Unique Trade Validation",
        "Previous Close Consistency"
    ]
    assert all(check["status"] == "PASS" for check in checks)


def test_quality_security_master_includes_summary_checks(
    client,
    auth_token,
    monkeypatch
):
    security_master_data = pd.DataFrame({
        "price": [100, 0, 200],
        "duration": [1, -1, 2],
        "convexity": [10, -1, 5],
        "ssm_id": ["A", "A", None],
        "name": ["Alpha", "Alpha", "Beta"],
        "isin": ["ISIN1", "ISIN1", "ISIN2"],
        "issuer_country": ["US", None, "IN"]
    })
    monkeypatch.setattr(
        "app.load_table",
        lambda datatype: security_master_data
    )

    response = client.get(
        "/api/quality",
        query_string={"datatype": "security_master"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    checks = {
        check["check_name"]: check
        for check in response.get_json()["checks"]
    }
    assert len(checks) == 5
    assert checks["Numeric Validation"]["status"] == "FAIL"
    assert checks["Duplicate SSM_ID"]["offending_count"] == 2
    assert checks["Duplicate Name/ISIN"]["offending_count"] == 2
    assert checks["Completeness"]["status"] == "FAIL"
    assert checks["Completeness"]["offending_count"] == 2
    assert checks["Identifier Uniqueness"]["status"] == "FAIL"
    assert checks["Identifier Uniqueness"]["offending_count"] == 3
