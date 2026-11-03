
from app.integrations.ecommerce_client import ecommerce_client


def get_all_products():
    """Retrieve all products from the catalog."""
    return ecommerce_client.get_all_products()


def get_product(product_id: int):
    """Retrieve a product using its ID."""
    return ecommerce_client.get_product(product_id)


def get_products_by_category(category: str):
    """Retrieve products belonging to a category."""
    return ecommerce_client.get_products_by_category(category)


def create_product(
    title: str,
    price: float,
    description: str,
    category: str,
    image: str = "",
):
    """Create a new product."""
    product_data = {
        "title": title,
        "price": price,
        "description": description,
        "category": category,
        "image": image,
    }

    return ecommerce_client.create_product(product_data)
