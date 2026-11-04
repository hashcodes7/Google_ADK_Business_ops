"""Google ADK Inbound Adapter: Exposes controlled tools to the Agent using shared application services."""
from app.services.product_service import product_service
from app.core.security import create_security_context


def get_all_products() -> list:
    """Get all products from the catalog."""
    context = create_security_context(actor="agent")
    return product_service.get_all_products(context=context)


def get_product(product_id: int) -> dict:
    """Get a product by its ID."""
    context = create_security_context(actor="agent")
    return product_service.get_product(product_id=product_id, context=context)


def get_products_by_category(category: str) -> list:
    """Get products belonging to a category."""
    context = create_security_context(actor="agent")
    return product_service.get_products_by_category(category=category, context=context)


def create_product(
    title: str,
    price: float,
    description: str,
    category: str,
    image: str = ""
) -> dict:
    """Create a new product."""
    context = create_security_context(actor="agent")
    return product_service.create_product(
        title=title,
        price=price,
        description=description,
        category=category,
        image=image,
        context=context,
    )
