import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import product_service, cart_service


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_products(client, monkeypatch):
    sample = [{"id": 1, "title": "Laptop", "price": 999,
               "description": "Test laptop", "category": "electronics",
               "image": ""}]

    monkeypatch.setattr(product_service, "get_all_products", lambda: sample)

    response = client.get("/api/v1/products/")

    assert response.status_code == 200
    assert response.json() == sample


def test_get_product(client, monkeypatch):
    sample = {"id": 1, "title": "Laptop", "price": 999,
              "description": "Test laptop", "category": "electronics",
              "image": ""}

    monkeypatch.setattr(product_service, "get_product", lambda pid: sample)

    response = client.get("/api/v1/products/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_products_by_category(client, monkeypatch):
    sample = [{"id": 1, "title": "Laptop", "price": 999,
               "description": "Test laptop", "category": "electronics",
               "image": ""}]

    monkeypatch.setattr(
        product_service, "get_products_by_category", lambda category: sample
    )

    response = client.get("/api/v1/products/category/electronics")

    assert response.status_code == 200
    assert response.json()[0]["category"] == "electronics"


def test_create_product(client, monkeypatch):
    sample = {"id": 101, "title": "Test Laptop", "price": 999,
              "description": "Test product", "category": "electronics",
              "image": ""}

    monkeypatch.setattr(
        product_service, "create_product", lambda **kwargs: sample
    )

    payload = {
        "title": "Test Laptop",
        "price": 999,
        "description": "Test product",
        "category": "electronics",
        "image": ""
    }

    response = client.post("/api/v1/products/", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == 101


def test_get_carts(client, monkeypatch):
    sample = [{"id": 1, "userId": 1, "products": []}]

    monkeypatch.setattr(cart_service, "get_all_carts", lambda: sample)

    response = client.get("/api/v1/carts/")

    assert response.status_code == 200
    assert response.json() == sample