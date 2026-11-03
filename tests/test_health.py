from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data == {
            "status": "healthy",
            "service": "business-dashboard",
        }
        print(f"\n💚 [Result] Health endpoint -> test_health.py -> GET /api/v1/health -> returned HTTP {response.status_code} with response payload: {data}")


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "application" in data
        assert "version" in data
        print(f"\n💚 [Result] Root endpoint -> test_health.py -> GET / -> returned HTTP {response.status_code} with response payload: {data}")
