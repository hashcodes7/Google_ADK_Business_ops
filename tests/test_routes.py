from fastapi.testclient import TestClient
from app.main import app


def test_get_all_products_route(monkeypatch):
    mock_catalog = [
        {"id": 1, "title": "Backpack", "price": 49.99, "description": "Durable", "category": "bags", "image": ""}
    ]
    from app.services import product_service
    monkeypatch.setattr(product_service, "get_all_products", lambda: mock_catalog)

    with TestClient(app) as client:
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        print(f"\n💚 [Result] GET /api/v1/products/ -> routes/products.py -> returned HTTP {response.status_code} with {len(data)} items")


def test_get_single_product_route(monkeypatch):
    mock_item = {"id": 1, "title": "Backpack", "price": 49.99, "description": "Durable", "category": "bags", "image": ""}
    from app.services import product_service
    monkeypatch.setattr(product_service, "get_product", lambda pid: mock_item)

    with TestClient(app) as client:
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        print(f"\n💚 [Result] GET /api/v1/products/1 -> routes/products.py -> returned HTTP {response.status_code} for item '{data['title']}'")


def test_create_product_route(monkeypatch):
    mock_created = {"id": 99, "title": "Keyboard", "price": 89.0, "description": "Mechanical", "category": "electronics", "image": ""}
    from app.services import product_service
    monkeypatch.setattr(product_service, "create_product", lambda **kwargs: mock_created)

    payload = {"title": "Keyboard", "price": 89.0, "description": "Mechanical", "category": "electronics"}
    with TestClient(app) as client:
        response = client.post("/api/v1/products/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 99
        print(f"\n💚 [Result] POST /api/v1/products/ -> routes/products.py -> returned HTTP {response.status_code} created ID={data['id']}")


def test_get_all_carts_route(monkeypatch):
    mock_carts = [{"id": 1, "userId": 2, "date": "2020-03-02", "products": []}]
    from app.services import cart_service
    monkeypatch.setattr(cart_service, "get_all_carts", lambda: mock_carts)

    with TestClient(app) as client:
        response = client.get("/api/v1/carts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print(f"\n💚 [Result] GET /api/v1/carts/ -> routes/carts.py -> returned HTTP {response.status_code} with {len(data)} carts")
