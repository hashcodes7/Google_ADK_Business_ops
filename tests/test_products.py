import pytest
from app.schemas.product import ProductCreate, ProductResponse
from app.services import product_service


def test_product_create_schema_validation():
    product = ProductCreate(
        title="Valid Product",
        price=19.99,
        description="A high quality product",
        category="electronics",
    )
    assert product.title == "Valid Product"
    assert product.price == 19.99
    assert product.image == ""
    print(f"\n💚 [Result] Schema validation -> test_products.py -> ProductCreate() -> validated payload: title='{product.title}', price=${product.price}")


def test_product_create_schema_invalid_price():
    with pytest.raises(Exception) as excinfo:
        ProductCreate(
            title="Invalid",
            price=-10.0,
            description="desc",
            category="cat",
        )
    print(f"\n💚 [Result] Negative price validation -> test_products.py -> ProductCreate(price=-10.0) -> rejected with {type(excinfo.value).__name__}")


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
    print(f"\n💚 [Result] Response serialization -> test_products.py -> ProductResponse() -> serialized ID={res.id}, title='{res.title}'")


def test_product_service_mock(monkeypatch):
    sample_data = {
        "id": 101,
        "title": "Mock Product",
        "price": 25.0,
        "description": "Mock desc",
        "category": "books",
        "image": "",
    }

    from app.integrations.ecommerce_client import ecommerce_client

    monkeypatch.setattr(ecommerce_client, "get_product", lambda pid: sample_data)

    result = product_service.get_product(101)
    assert result["id"] == 101
    assert result["title"] == "Mock Product"
    print(f"\n💚 [Result] Service call -> test_products.py -> product_service.get_product(101) -> returned: ID={result['id']}, Title='{result['title']}'")
