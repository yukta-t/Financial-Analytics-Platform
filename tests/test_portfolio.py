import pandas as pd
import pytest

import app as backend_module
from backend.services.portfolio_service import (
    PortfolioInputError,
    get_available_tickers,
    simulate_portfolio
)


@pytest.fixture
def portfolio_stock_data():
    return pd.DataFrame({
        "ticker": ["aapl", "aapl", "aapl", "msft", "msft", "msft"],
        "date": pd.to_datetime([
            "2026-01-01", "2026-01-02", "2026-01-03",
            "2026-01-01", "2026-01-02", "2026-01-03"
        ]),
        "close": [100, 110, 99, 100, 110, 121]
    })


def test_available_tickers_are_dynamic_normalized_and_sorted(portfolio_stock_data):
    tickers = get_available_tickers(portfolio_stock_data)

    assert tickers == ["AAPL", "MSFT"]


def test_simulation_calculates_weighted_metrics_and_chart(portfolio_stock_data):
    result = simulate_portfolio(
        portfolio_stock_data,
        [
            {"ticker": "AAPL", "weight": 50},
            {"ticker": "MSFT", "weight": 50}
        ]
    )

    assert result["expected_return"] == 5.0
    assert result["volatility"] > 0
    assert result["risk_score"] == "High"
    assert result["chart"] == {
        "labels": ["AAPL", "MSFT"],
        "values": [50.0, 50.0]
    }


@pytest.mark.parametrize(
    "closes, expected_risk",
    [
        ([100, 101, 102.01], "Low"),
        ([100, 100.5, 100], "Medium")
    ]
)
def test_simulation_assigns_low_and_medium_risk_scores(closes, expected_risk):
    stock_data = pd.DataFrame({
        "ticker": ["TEST", "TEST", "TEST"],
        "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
        "close": closes
    })

    result = simulate_portfolio(
        stock_data,
        [{"ticker": "TEST", "weight": 100}]
    )

    assert result["risk_score"] == expected_risk


@pytest.mark.parametrize(
    "holdings",
    [
        [],
        [{"ticker": "AAPL", "weight": 40}],
        [
            {"ticker": "AAPL", "weight": 50},
            {"ticker": "aapl", "weight": 50}
        ],
        [{"ticker": "UNKNOWN", "weight": 100}],
        [{"ticker": "AAPL", "weight": True}]
    ]
)
def test_simulation_rejects_invalid_holdings(portfolio_stock_data, holdings):
    with pytest.raises(PortfolioInputError):
        simulate_portfolio(portfolio_stock_data, holdings)


def test_portfolio_securities_endpoint_requires_authentication(client):
    response = client.get("/api/portfolio/securities")

    assert response.status_code == 401


def test_portfolio_page_exposes_new_simulator_ui(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'id="portfolioPage"' in response.data
    assert b'id="portfolioNavBtn"' in response.data
    assert b'id="portfolioAllocationChart"' in response.data


def test_portfolio_endpoints_use_stock_data(client, auth_token, monkeypatch, portfolio_stock_data):
    monkeypatch.setattr(
        backend_module,
        "load_table",
        lambda datatype: portfolio_stock_data if datatype == "stock" else pytest.fail(
            "Portfolio endpoints must load the STOCK dataset"
        )
    )
    headers = {"Authorization": f"Bearer {auth_token}"}

    securities_response = client.get(
        "/api/portfolio/securities",
        headers=headers
    )
    simulation_response = client.post(
        "/api/portfolio/simulate",
        json={
            "holdings": [
                {"ticker": "AAPL", "weight": 40},
                {"ticker": "MSFT", "weight": 60}
            ]
        },
        headers=headers
    )

    assert securities_response.status_code == 200
    assert securities_response.get_json()["securities"] == ["AAPL", "MSFT"]
    assert simulation_response.status_code == 200
    assert simulation_response.get_json()["expected_return"] == 6.0


def test_simulation_endpoint_rejects_incomplete_allocation(client, auth_token, monkeypatch, portfolio_stock_data):
    monkeypatch.setattr(
        backend_module,
        "load_table",
        lambda datatype: portfolio_stock_data
    )

    response = client.post(
        "/api/portfolio/simulate",
        json={"holdings": [{"ticker": "AAPL", "weight": 40}]},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Portfolio allocations must sum to 100%"
