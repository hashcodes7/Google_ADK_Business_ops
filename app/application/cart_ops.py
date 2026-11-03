from typing import Any
from app.core.security import SecurityContext, create_security_context, require_permission
from app.integrations.ecommerce_client import ecommerce_client
from app.ports.ecommerce_port import EcommercePort


class CartOperations:
    """Shared application operations for shopping carts."""

    def __init__(self, port: EcommercePort = ecommerce_client):
        self.port = port

    def get_all_carts(self, context: SecurityContext | None = None) -> list[dict[str, Any]]:
        ctx = context or create_security_context()
        # Least privilege: Example of centralized authorization
        require_permission(ctx, allowed_actors=["human", "agent"], required_role="Business")
        return self.port.get_all_carts()


cart_operations = CartOperations()
