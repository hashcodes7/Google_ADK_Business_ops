from typing import Any
from app.core.security import SecurityContext, create_security_context, require_permission
from app.integrations.ecommerce_client import ecommerce_client
from app.schemas.product import ProductCreate, ProductResponse
from app.ports.ecommerce_port import EcommercePort


class ProductOperations:
    """Shared application operations for product catalog."""

    def __init__(self, port: EcommercePort = ecommerce_client):
        self.port = port

    def get_all_products(self, context: SecurityContext | None = None) -> list[dict[str, Any]]:
        ctx = context or create_security_context()
        require_permission(ctx, allowed_actors=["human", "agent"], required_role="Business")
        return self.port.get_all_products()

    def get_product(self, product_id: int, context: SecurityContext | None = None) -> dict[str, Any]:
        ctx = context or create_security_context()
        require_permission(ctx, allowed_actors=["human", "agent"], required_role="Business")
        return self.port.get_product(product_id)

    def get_products_by_category(self, category: str, context: SecurityContext | None = None) -> list[dict[str, Any]]:
        ctx = context or create_security_context()
        require_permission(ctx, allowed_actors=["human", "agent"], required_role="Business")
        return self.port.get_products_by_category(category)

    def create_product(
        self,
        title: str,
        price: float,
        description: str,
        category: str,
        image: str = "",
        context: SecurityContext | None = None,
    ) -> dict[str, Any]:
        ctx = context or create_security_context()
        require_permission(ctx, allowed_actors=["human", "agent"], required_role="Business")

        # Validate business input via shared schema
        payload = ProductCreate(
            title=title,
            price=price,
            description=description,
            category=category,
            image=image,
        )
        return self.port.create_product(payload.model_dump())


product_operations = ProductOperations()
