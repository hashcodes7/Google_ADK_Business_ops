from app.application.product_ops import product_operations
from app.core.security import create_security_context


def get_all_products(context=None):
    """Retrieve all products from the catalog."""
    return product_operations.get_all_products(context)


def get_product(product_id: int, context=None):
    """Retrieve a product using its ID."""
    return product_operations.get_product(product_id, context)


def get_products_by_category(category: str, context=None):
    """Retrieve products belonging to a category."""
    return product_operations.get_products_by_category(category, context)


def create_product(
    title: str,
    price: float,
    description: str,
    category: str,
    image: str = "",
    context=None,
):
    """Create a new product."""
    return product_operations.create_product(
        title=title,
        price=price,
        description=description,
        category=category,
        image=image,
        context=context,
    )
