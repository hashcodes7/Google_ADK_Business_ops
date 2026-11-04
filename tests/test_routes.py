from fastapi.testclient import TestClient
from app.main import app

AUTH_HEADER_BUSINESS = {"Authorization": "Bearer token-business-49"}
AUTH_HEADER_ADMIN = {"Authorization": "Bearer token-admin-01"}


def test_missing_auth_header_rejected():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/")
        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["error"]
        print(f"\n💚 [Result] Auth Guard -> test_routes.py -> Missing token rejected with HTTP 401")


def test_invalid_auth_token_rejected():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401
        assert "Invalid or expired" in response.json()["error"]
        print(f"\n💚 [Result] Auth Guard -> test_routes.py -> Invalid token rejected with HTTP 401")


def test_get_all_products_route(monkeypatch):
    mock_catalog = [
        {"id": 1, "title": "Backpack", "price": 49.99, "description": "Durable", "category": "bags", "image": ""}
    ]
    from app.services.product_service import product_service
    monkeypatch.setattr(product_service, "get_all_products", lambda context=None: mock_catalog)

    with TestClient(app) as client:
        response = client.get("/api/v1/products/", headers=AUTH_HEADER_BUSINESS)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        print(f"\n💚 [Result] GET /api/v1/products/ -> routes/products.py -> returned HTTP {response.status_code} with {len(data)} items")


def test_get_single_product_route(monkeypatch):
    mock_item = {"id": 1, "title": "Backpack", "price": 49.99, "description": "Durable", "category": "bags", "image": ""}
    from app.services.product_service import product_service
    monkeypatch.setattr(product_service, "get_product", lambda pid, context=None: mock_item)

    with TestClient(app) as client:
        response = client.get("/api/v1/products/1", headers=AUTH_HEADER_BUSINESS)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        print(f"\n💚 [Result] GET /api/v1/products/1 -> routes/products.py -> returned HTTP {response.status_code} for item '{data['title']}'")


def test_create_product_route_business_role_forbidden():
    payload = {"title": "Keyboard", "price": 89.0, "description": "Mechanical", "category": "electronics"}
    with TestClient(app) as client:
        # Business role lacks products:write permission -> HTTP 403
        response = client.post("/api/v1/products/", json=payload, headers=AUTH_HEADER_BUSINESS)
        assert response.status_code == 403
        assert "lacks required permission 'products:write'" in response.json()["error"]
        print(f"\n💚 [Result] RBAC Guard -> test_routes.py -> POST /api/v1/products/ rejected with HTTP 403 for Business role")


def test_create_product_route_admin_role_success(monkeypatch):
    mock_created = {"id": 99, "title": "Keyboard", "price": 89.0, "description": "Mechanical", "category": "electronics", "image": ""}
    from app.services.product_service import product_service
    monkeypatch.setattr(product_service, "create_product", lambda **kwargs: mock_created)

    payload = {"title": "Keyboard", "price": 89.0, "description": "Mechanical", "category": "electronics"}
    with TestClient(app) as client:
        # Admin role has products:write permission -> HTTP 200
        response = client.post("/api/v1/products/", json=payload, headers=AUTH_HEADER_ADMIN)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 99
        print(f"\n💚 [Result] POST /api/v1/products/ -> routes/products.py -> returned HTTP {response.status_code} created ID={data['id']} for Admin")


def test_get_all_carts_route(monkeypatch):
    mock_carts = [{"id": 1, "userId": 2, "date": "2020-03-02", "products": []}]
    from app.services.cart_service import cart_service
    monkeypatch.setattr(cart_service, "get_all_carts", lambda context=None: mock_carts)

    with TestClient(app) as client:
        response = client.get("/api/v1/carts/", headers=AUTH_HEADER_BUSINESS)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print(f"\n💚 [Result] GET /api/v1/carts/ -> routes/carts.py -> returned HTTP {response.status_code} with {len(data)} carts")
