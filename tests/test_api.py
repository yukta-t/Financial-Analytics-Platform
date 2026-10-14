"""Integration tests for the Flask API endpoints defined in backend/app.py."""


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