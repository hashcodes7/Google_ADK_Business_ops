from typing import Any
from app.core.exceptions import AuthenticationException
from app.core.security import SecurityContext, Permission, require_permission
from app.integrations.ecommerce_client import ecommerce_client
from app.schemas.product import ProductCreate
from app.ports.ecommerce_port import EcommercePort


class ProductService:
    """Application Service handling business capabilities for the product catalog."""

    def __init__(self, port: EcommercePort = ecommerce_client):
        self.port = port

    def get_all_products(self, context: SecurityContext = None) -> list[dict[str, Any]]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.PRODUCTS_READ)
        return self.port.get_all_products()

    def get_product(self, product_id: int, context: SecurityContext = None) -> dict[str, Any]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.PRODUCTS_READ)
        return self.port.get_product(product_id)

    def get_products_by_category(self, category: str, context: SecurityContext = None) -> list[dict[str, Any]]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.PRODUCTS_READ)
        return self.port.get_products_by_category(category)

    def create_product(
        self,
        title: str,
        price: float,
        description: str,
        category: str,
        image: str = "",
        context: SecurityContext = None,
    ) -> dict[str, Any]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.PRODUCTS_WRITE)

        # Centralized schema validation
        payload = ProductCreate(
            title=title,
            price=price,
            description=description,
            category=category,
            image=image,
        )
        return self.port.create_product(payload.model_dump())


product_service = ProductService()

def get_all_products(context: SecurityContext = None):
    return product_service.get_all_products(context=context)

def get_product(product_id: int, context: SecurityContext = None):
    return product_service.get_product(product_id=product_id, context=context)

def get_products_by_category(category: str, context: SecurityContext = None):
    return product_service.get_products_by_category(category=category, context=context)

def create_product(title: str, price: float, description: str, category: str, image: str = "", context: SecurityContext = None):
    return product_service.create_product(title=title, price=price, description=description, category=category, image=image, context=context)
