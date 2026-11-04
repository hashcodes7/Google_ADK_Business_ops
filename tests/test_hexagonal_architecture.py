import pytest
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.user_service import UserService
from app.core.security import SecurityContext, Role, Permission
from app.core.exceptions import UnauthorizedException, AuthenticationException
from agents.tools import product_tools, cart_tools


class FakeEcommercePort:
    def __init__(self):
        self.products = [
            {"id": 1, "title": "Test Item", "price": 10.0, "description": "desc", "category": "cat", "image": ""}
        ]
        self.carts = [{"id": 1, "userId": 1, "products": []}]
        self.users = []

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

    def get_cart_by_id(self, cart_id: int):
        return {"id": cart_id, "userId": 1, "products": [{"id": 1, "quantity": 2}]}

    def create_user(self, user_data: dict):
        new_u = dict(user_data)
        new_u["id"] = 12
        return new_u


def test_missing_security_context_raises_authentication_exception():
    port = FakeEcommercePort()
    service = ProductService(port=port)
    with pytest.raises(AuthenticationException) as excinfo:
        service.get_all_products(context=None)
    assert "Security context is required" in str(excinfo.value)
    print(f"\n💚 [Result] Auth Guard -> test_hexagonal_architecture.py -> None context rejected with AuthenticationException")


def test_business_role_permitted_to_read():
    port = FakeEcommercePort()
    service = ProductService(port=port)
    ctx = SecurityContext(user_id="User_49", role=Role.BUSINESS)
    
    res = service.get_all_products(context=ctx)
    assert len(res) == 1
    print(f"\n💚 [Result] RBAC Read -> test_hexagonal_architecture.py -> Role.BUSINESS permitted for PRODUCTS_READ")


def test_business_role_denied_write_permission():
    port = FakeEcommercePort()
    service = ProductService(port=port)
    ctx = SecurityContext(user_id="User_49", role=Role.BUSINESS)
    with pytest.raises(UnauthorizedException) as excinfo:
        service.create_product(
            title="Unauthorized Item",
            price=29.99,
            description="desc",
            category="electronics",
            context=ctx,
        )
    assert "lacks required permission 'products:write'" in str(excinfo.value)
    print(f"\n💚 [Result] RBAC Selective Guard -> test_hexagonal_architecture.py -> Role.BUSINESS denied PRODUCTS_WRITE")


def test_user_only_create_user_admin_required():
    port = FakeEcommercePort()
    user_svc = UserService(port=port)

    # Business role is denied
    ctx_biz = SecurityContext(user_id="User_49", role=Role.BUSINESS)
    with pytest.raises(UnauthorizedException) as exc:
        user_svc.create_user(username="newbie", email="new@corp.com", password="secret123", context=ctx_biz)
    assert "lacks required permission 'users:write'" in str(exc.value)

    # Admin role is allowed
    ctx_admin = SecurityContext(user_id="Admin_01", role=Role.ADMIN)
    res = user_svc.create_user(username="newbie", email="new@corp.com", password="secret123", context=ctx_admin)
    assert res["id"] == 12
    print(f"\n💚 [Result] User-Only API -> test_hexagonal_architecture.py -> POST /users restricted to Admin, denied to Business")


def test_agent_only_inspect_cart_by_id():
    port = FakeEcommercePort()
    cart_svc = CartService(port=port)
    ctx = SecurityContext(user_id="User_49", role=Role.BUSINESS)

    cart = cart_svc.get_cart_by_id(cart_id=5, context=ctx)
    assert cart["id"] == 5
    assert len(cart["products"]) == 1
    print(f"\n💚 [Result] Agent-Only API -> test_hexagonal_architecture.py -> inspect_cart_by_id executed successfully via shared service")


def test_agent_inbound_adapter_tools(monkeypatch):
    from agents.tools import product_tools, cart_tools

    sample_products = [{"id": 1, "title": "Agent Item", "price": 20.0, "description": "d", "category": "c", "image": ""}]
    sample_cart = {"id": 10, "userId": 1, "products": [{"id": 2}]}

    monkeypatch.setattr(product_tools.product_service, "get_all_products", lambda context=None: sample_products)
    monkeypatch.setattr(cart_tools.cart_service, "get_cart_by_id", lambda cart_id, context=None: sample_cart)

    products = product_tools.get_all_products()
    cart = cart_tools.inspect_cart_by_id(cart_id=10)

    assert len(products) == 1
    assert cart["id"] == 10
    print(f"\n💚 [Result] Agent Inbound Adapter -> test_hexagonal_architecture.py -> ADK tools executed with agent context")
