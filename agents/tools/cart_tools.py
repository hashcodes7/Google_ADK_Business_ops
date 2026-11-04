"""Google ADK Inbound Adapter: Exposes controlled shopping cart tools using shared application services."""
from app.services.cart_service import cart_service
from app.core.security import create_security_context


def get_all_carts() -> list:
    """Get all shopping carts."""
    context = create_security_context()
    return cart_service.get_all_carts(context=context)


def inspect_cart_by_id(cart_id: int) -> dict:
    """
    Agent Only Tool:
    Allows the AI agent to look up details of a customer's specific shopping cart
    during customer assistance or cart recovery conversations.
    (Omitted from REST endpoints).
    """
    context = create_security_context()
    return cart_service.get_cart_by_id(cart_id=cart_id, context=context)
