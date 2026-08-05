"""Phase 0 smoke test.

Verifies that the application factory builds, configuration loads from the
environment, and the health endpoint responds. This is the canary: if it
fails, the scaffold itself is broken and no later phase can be trusted.
"""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_ok():
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] in {"development", "production"}
