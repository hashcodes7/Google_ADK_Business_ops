import pytest
from app.schemas.product import ProductCreate, ProductResponse
from app.services import product_service


def test_product_create_schema_validation():
    # Valid schema creation
    product = ProductCreate(
        title="Valid Product",
        price=19.99,
        description="A high quality product",
        category="electronics",
    )
    assert product.title == "Valid Product"
    assert product.price == 19.99
    assert product.image == ""


def test_product_create_schema_invalid_price():
    # Negative price should trigger validation error
    with pytest.raises(Exception):
        ProductCreate(
            title="Invalid",
            price=-10.0,
            description="desc",
            category="cat",
        )


def test_product_response_schema():
    res = ProductResponse(
        id=42,
        title="Laptop Stand",
        price=49.99,
        description="Ergonomic aluminum stand",
        category="electronics",
        image="https://example.com/item.jpg",
    )
    assert res.id == 42
    assert res.price == 49.99


def test_product_service_mock(monkeypatch):
    sample_data = {
        "id": 101,
        "title": "Mock Product",
        "price": 25.0,
        "description": "Mock desc",
        "category": "books",
        "image": "",
    }

    # Test service integration with mocked client
    from app.integrations.ecommerce_client import ecommerce_client

    monkeypatch.setattr(ecommerce_client, "get_product", lambda pid: sample_data)

    result = product_service.get_product(101)
    assert result["id"] == 101
    assert result["title"] == "Mock Product"
