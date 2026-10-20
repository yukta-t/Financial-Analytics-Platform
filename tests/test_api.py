"""Integration tests for the Flask API endpoints defined in backend/app.py."""

import math

import pandas as pd
import pytest

import app as backend_app


@pytest.fixture
def stock_chart_data():
    return pd.DataFrame({
        "date": [
            "2025-01-03",
            "2025-01-01",
            "2025-01-03",
            "2025-01-02",
            "2025-01-02",
            "2025-01-01"
        ],
        "ticker": ["MSFT", "AAPL", "AAPL", "MSFT", "XOM", "XOM"],
        "close": [220.0, 100.0, 110.0, 200.0, 50.0, 45.0],
        "dividends": [0.5, 0.2, 0.2, 0.5, 0.1, 0.1]
    })


def test_health_check_no_auth_required(client):

    response = client.get("/api/health")

    assert response.status_code == 200

    body = response.get_json()

    assert body["status"] == "ok"
    assert "timestamp" in body


def test_login_with_valid_credentials_returns_token(client):

    response = client.post(
        "/api/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["status"] == "ok"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


def test_login_with_invalid_credentials_returns_401(client):

    response = client.post(
        "/api/login",
        json={
            "username": "admin",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401

    body = response.get_json()

    assert body["status"] == "error"


def test_metrics_requires_token(client):

    response = client.get(
        "/api/metrics",
        query_string={"datatype": "stock"}
    )

    assert response.status_code == 401


def test_metrics_with_invalid_token_returns_401(client):

    response = client.get(
        "/api/metrics",
        query_string={"datatype": "stock"},
        headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


def test_metrics_returns_stock_metrics_list(client, auth_token):

    response = client.get(
        "/api/metrics",
        query_string={"datatype": "stock"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["status"] == "ok"
    ids = {metric["id"] for metric in body["metrics"]}
    assert "daily_return" in ids
    assert "sma" in ids


def test_metrics_returns_bonds_metrics_list(client, auth_token):

    response = client.get(
        "/api/metrics",
        query_string={"datatype": "bonds"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    body = response.get_json()

    ids = {metric["id"] for metric in body["metrics"]}
    assert "ytm" in ids


def test_metrics_with_invalid_datatype_returns_400(client, auth_token):

    response = client.get(
        "/api/metrics",
        query_string={"datatype": "not_a_real_datatype"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["status"] == "error"


def test_execute_requires_token(client):

    response = client.post(
        "/api/execute",
        json={
            "datatype": "stock",
            "metric_id": "daily_return"
        }
    )

    assert response.status_code == 401


def test_execute_stock_daily_return_succeeds(client, auth_token):

    response = client.post(
        "/api/execute",
        json={
            "datatype": "stock",
            "metric_id": "daily_return"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["status"] == "ok"
    assert "daily_return" in body["columns"]
    assert isinstance(body["rows"], list)
    assert len(body["rows"]) > 0


@pytest.mark.parametrize("metric_id", ["daily_return", "log_return"])
def test_stock_return_chart_has_a_null_gapped_series_per_ticker(
    client,
    auth_token,
    monkeypatch,
    stock_chart_data,
    metric_id
):
    monkeypatch.setattr(
        backend_app,
        "load_table",
        lambda datatype: stock_chart_data.copy()
    )

    response = client.post(
        "/api/execute",
        json={"datatype": "stock", "metric_id": metric_id},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    body = response.get_json()
    chart = body["chart"]

    assert body["columns"] == [
        "date",
        "ticker",
        "close",
        "dividends",
        metric_id
    ]
    assert len(body["rows"]) == len(stock_chart_data)
    assert body["rows"][0][body["columns"].index(metric_id)] == ""
    assert chart["type"] == "line"
    assert chart["labels"] == ["2025-01-01", "2025-01-02", "2025-01-03"]
    assert [dataset["label"] for dataset in chart["datasets"]] == [
        "AAPL",
        "MSFT",
        "XOM"
    ]

    datasets = {dataset["label"]: dataset["data"] for dataset in chart["datasets"]}
    expected_change = 0.1 if metric_id == "daily_return" else math.log(1.1)

    assert datasets["AAPL"][:2] == [None, None]
    assert datasets["AAPL"][2] == pytest.approx(expected_change)
    assert datasets["MSFT"] == [None, None, pytest.approx(expected_change)]
    assert datasets["XOM"][0] is None
    assert datasets["XOM"][1] == pytest.approx(
        (50.0 / 45.0 - 1.0)
        if metric_id == "daily_return"
        else math.log(50.0 / 45.0)
    )
    assert datasets["XOM"][2] is None


@pytest.mark.parametrize(
    "metric_id",
    ["sma", "ema", "volatility", "dividend_yield"]
)
def test_stock_time_series_metrics_return_ticker_datasets(
    client,
    auth_token,
    monkeypatch,
    stock_chart_data,
    metric_id
):
    monkeypatch.setattr(
        backend_app,
        "load_table",
        lambda datatype: stock_chart_data.copy()
    )

    response = client.post(
        "/api/execute",
        json={
            "datatype": "stock",
            "metric_id": metric_id,
            "params": {"window": 2}
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    body = response.get_json()

    assert [dataset["label"] for dataset in body["chart"]["datasets"]] == [
        "AAPL",
        "MSFT",
        "XOM"
    ]
    assert all(
        len(dataset["data"]) == len(body["chart"]["labels"])
        for dataset in body["chart"]["datasets"]
    )
    assert len(body["rows"]) == len(stock_chart_data)


def test_bond_chart_keeps_legacy_single_series_payload(
    client,
    auth_token,
    monkeypatch
):
    bond_data = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "face_value": [1000.0, 1000.0],
        "coupon_rate": [0.05, 0.04],
        "price": [980.0, 1010.0],
        "years_to_maturity": [5, 3]
    })
    monkeypatch.setattr(
        backend_app,
        "load_table",
        lambda datatype: bond_data.copy()
    )

    response = client.post(
        "/api/execute",
        json={"datatype": "bonds", "metric_id": "ytm"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    chart = response.get_json()["chart"]
    assert set(chart) == {"labels", "values"}
    assert chart["labels"] == bond_data["date"].tolist()
    assert len(chart["values"]) == len(bond_data)


def test_execute_stock_vwap_succeeds(client, auth_token):

    response = client.post(
        "/api/execute",
        json={
            "datatype": "stock",
            "metric_id": "vwap"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["status"] == "ok"
    assert body["columns"] == ["vwap"]
    assert len(body["rows"]) == 1


def test_execute_with_unknown_metric_returns_400(client, auth_token):

    response = client.post(
        "/api/execute",
        json={
            "datatype": "stock",
            "metric_id": "not_a_real_metric"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["status"] == "error"


def test_execute_with_missing_metric_id_returns_400(client, auth_token):

    response = client.post(
        "/api/execute",
        json={
            "datatype": "stock"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["status"] == "error"