import pytest
from fastapi.testclient import TestClient
from src.dependencies import get_fakestore_client
from src.main import app
from src.schemas.product import Product, Rating
from src.clients.fakestore_client import (
    FakeStoreItemNotFoundError,
    FakeStoreUpstreamError,
)

SAMPLE_PRODUCTS = [
    Product(
        id=1,
        title="Test Backpack",
        price=109.95,
        description="A great everyday backpack.",
        category="men's clothing",
        image="https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
        rating=Rating(rate=3.9, count=120),
    ),
    Product(
        id=2,
        title="Slim Fit T-Shirt",
        price=22.3,
        description="Slim-fitting style, contrast raglan long sleeve.",
        category="men's clothing",
        image="https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UT_.jpg",
        rating=Rating(rate=4.1, count=259),
    ),
]


class MockFakeStoreClient:
    """Mock client for testing API routes without invoking external networks."""

    async def get_products(self, limit=None, sort=None):
        products = list(SAMPLE_PRODUCTS)
        if limit is not None:
            products = products[:limit]
        return products

    async def get_product(self, product_id: int):
        for p in SAMPLE_PRODUCTS:
            if p.id == product_id:
                return p
        raise FakeStoreItemNotFoundError(f"Product {product_id} not found")

    async def get_categories(self):
        return ["electronics", "jewelery", "men's clothing", "women's clothing"]

    async def get_products_by_category(self, category: str, limit=None, sort=None):
        matched = [p for p in SAMPLE_PRODUCTS if p.category == category]
        if limit is not None:
            matched = matched[:limit]
        return matched


@pytest.fixture(autouse=True)
def override_dependency():
    app.dependency_overrides[get_fakestore_client] = lambda: MockFakeStoreClient()
    yield
    app.dependency_overrides.clear()


def test_get_all_products():
    with TestClient(app) as client:
        response = client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Test Backpack"
        assert data[0]["price"] == 109.95


def test_get_products_with_limit():
    with TestClient(app) as client:
        response = client.get("/api/v1/products?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1


def test_get_product_by_id_success():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Backpack"


def test_get_product_by_id_not_found():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_get_categories():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/categories")
        assert response.status_code == 200
        data = response.json()
        assert "electronics" in data
        assert "men's clothing" in data


def test_get_products_by_category():
    with TestClient(app) as client:
        response = client.get("/api/v1/products/category/men's clothing")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["category"] == "men's clothing" for p in data)


def test_upstream_error_handling():
    class FailingClient:
        async def get_products(self, limit=None, sort=None):
            raise FakeStoreUpstreamError("FakeStore connection timeout", status_code=504)

    app.dependency_overrides[get_fakestore_client] = lambda: FailingClient()

    with TestClient(app) as client:
        response = client.get("/api/v1/products")
        assert response.status_code == 502
        assert "FakeStore connection timeout" in response.json()["detail"]
