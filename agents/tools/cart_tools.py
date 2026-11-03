"""Google ADK Inbound Adapter: Exposes controlled shopping cart tools using shared application operations."""
from app.application.cart_ops import cart_operations
from app.core.security import create_security_context


def get_all_carts() -> list:
    """Get all shopping carts."""
    context = create_security_context(actor="agent")
    return cart_operations.get_all_carts(context=context)
