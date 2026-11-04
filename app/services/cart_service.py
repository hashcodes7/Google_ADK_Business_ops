from typing import Any
from app.core.exceptions import AuthenticationException
from app.core.security import SecurityContext, Permission, require_permission
from app.integrations.ecommerce_client import ecommerce_client
from app.ports.ecommerce_port import EcommercePort


class CartService:
    """Application Service handling business capabilities for shopping carts."""

    def __init__(self, port: EcommercePort = ecommerce_client):
        self.port = port

    def get_all_carts(self, context: SecurityContext = None) -> list[dict[str, Any]]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.CARTS_READ)
        return self.port.get_all_carts()

    def get_cart_by_id(self, cart_id: int, context: SecurityContext = None) -> dict[str, Any]:
        """Inspect specific cart by ID (Used by Agent for customer assistance)."""
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.CARTS_READ)
        return self.port.get_cart_by_id(cart_id)


cart_service = CartService()

def get_all_carts(context: SecurityContext = None):
    return cart_service.get_all_carts(context=context)

def get_cart_by_id(cart_id: int, context: SecurityContext = None):
    return cart_service.get_cart_by_id(cart_id=cart_id, context=context)
