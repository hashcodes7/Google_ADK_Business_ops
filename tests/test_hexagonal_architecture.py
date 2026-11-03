import pytest
from app.application.product_ops import ProductOperations
from app.application.cart_ops import CartOperations
from app.core.security import SecurityContext
from app.core.exceptions import UnauthorizedException
from agents.tools import product_tools, cart_tools


class FakeEcommercePort:
    def __init__(self):
        self.products = [
            {"id": 1, "title": "Test Item", "price": 10.0, "description": "desc", "category": "cat", "image": ""}
        ]
        self.carts = [{"id": 1, "userId": 1, "products": []}]

    def get_all_products(self):
        return self.products

    def get_product(self, product_id: int):
        return self.products[0]

    def get_products_by_category(self, category: str):
        return [p for p in self.products if p["category"] == category]

    def create_product(self, product_data: dict):
        new_prod = dict(product_data)
        new_prod["id"] = 99
        return new_prod

    def get_all_carts(self):
        return self.carts


def test_shared_product_operations_authorization_success():
    port = FakeEcommercePort()
    ops = ProductOperations(port=port)
    ctx = SecurityContext(user_id="User_49", role="Business", actor="human")
    products = ops.get_all_products(context=ctx)
    assert len(products) == 1
    print(f"\n💚 [Result] Shared Ops -> test_hexagonal_architecture.py -> ProductOperations authorized for User_49 (role=Business, actor=human)")


def test_shared_product_operations_authorization_denied():
    port = FakeEcommercePort()
    ops = ProductOperations(port=port)
    # Actor/role mismatch should be rejected
    ctx = SecurityContext(user_id="User_49", role="Guest", actor="human")
    with pytest.raises(UnauthorizedException):
        ops.get_all_products(context=ctx)
    print(f"\n💚 [Result] Centralized Auth -> test_hexagonal_architecture.py -> Rejected role 'Guest' with UnauthorizedException")


def test_agent_inbound_adapter_tools(monkeypatch):
    from app.application.product_ops import product_operations
    from app.application.cart_ops import cart_operations

    sample_products = [{"id": 1, "title": "Agent Item", "price": 20.0, "description": "d", "category": "c", "image": ""}]
    sample_carts = [{"id": 1, "userId": 1, "products": []}]

    monkeypatch.setattr(product_operations, "get_all_products", lambda context=None: sample_products)
    monkeypatch.setattr(cart_operations, "get_all_carts", lambda context=None: sample_carts)

    products = product_tools.get_all_products()
    carts = cart_tools.get_all_carts()

    assert len(products) == 1
    assert len(carts) == 1
    print(f"\n💚 [Result] Agent Inbound Adapter -> test_hexagonal_architecture.py -> ADK tools executed with trusted actor='agent'")
