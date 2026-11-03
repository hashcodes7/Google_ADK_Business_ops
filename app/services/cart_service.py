from app.application.cart_ops import cart_operations


def get_all_carts(context=None):
    """Retrieve all shopping carts."""
    return cart_operations.get_all_carts(context)
