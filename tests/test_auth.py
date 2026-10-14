from backend.auth import (
    generate_token,
    verify_token
)


def test_generate_token(app):

    token = generate_token(
        "admin"
    )

    assert token is not None
    assert isinstance(token, str)


def test_verify_token(app):

    token = generate_token(
        "admin"
    )

    result = verify_token(token)

    assert result["valid"] is True
    assert result["user"] == "admin"


def test_invalid_token(app):

    result = verify_token(
        "fake_token"
    )

    assert result["valid"] is False


def test_protected_endpoint_requires_token(
    client
):

    response = client.get(
        "/api/metrics"
    )

    assert response.status_code == 401


def test_metrics_authorized(client, auth_token):

    response = client.get(
        "/api/metrics",
        query_string={
            "datatype": "stock"
        },
        headers={
            "Authorization":
            f"Bearer {auth_token}"
        }
    )

    assert response.status_code == 200