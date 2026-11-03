
from app.integrations.ecommerce_client import ecommerce_client


def get_all_carts():
    """Retrieve all shopping carts."""
    return ecommerce_client.get_all_carts()
