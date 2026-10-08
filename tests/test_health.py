from unittest.mock import patch


def test_health_probe(client):
    """Test /health liveness probe."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "PocketLedger"
    assert data["version"] == "0.1.0"

def test_readiness_probe_success(client):
    """Test /ready readiness probe with active DB connection."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"

def test_readiness_probe_failure(client):
    """Test /ready readiness probe when database connection fails (Item #15)."""
    with patch("app.routers.health.check_db_connection", return_value=False):
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["detail"] == "Database connectivity check failed"
