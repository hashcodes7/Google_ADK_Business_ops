import logging
import re
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_security_context
from app.core.security import SecurityContext
from agents.tools.product_tools import (
    get_all_products,
    get_product,
    get_products_by_category,
)
from agents.tools.cart_tools import (
    get_all_carts,
    inspect_cart_by_id,
)
from agents.tools.user_tools import (
    get_all_users,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["Assistant"])


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    reply: str
    tool_used: str | None = None


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_assistant(
    request: ChatMessageRequest,
    context: Annotated[SecurityContext, Depends(get_current_security_context)],
):
    """
    Handle natural language assistant inquiries by matching operational intents
    and executing the corresponding Google ADK agent tools with the agent security context.
    """
    msg = request.message.lower().strip()
    logger.info("Assistant received message from %s: %s", context.user_id, msg)

    # 0. Get All Users (Admin check)
    # Matches: "get all users", "users list", "show users", "all users"
    if "user" in msg and ("all" in msg or "list" in msg or "show" in msg or "get" in msg):
        result = get_all_users(context=context)
        if isinstance(result, str):
            # Permission denial message
            return ChatMessageResponse(
                reply=result,
                tool_used="get_all_users",
            )
        # Successfully fetched list
        user_lines = [f"• #{u.get('id')} {u.get('username')} ({u.get('email')})" for u in result[:8]]
        more = f"\n...and {len(result) - 8} more users." if len(result) > 8 else ""
        return ChatMessageResponse(
            reply=f"Retrieved {len(result)} registered users:\n\n" + "\n".join(user_lines) + more,
            tool_used="get_all_users",
        )

    # 1. Inspect Cart by ID (Agent-only capability)
    # Matches: "inspect cart #1", "cart #2", "check cart 1"
    cart_match = re.search(r"cart\s*(?:#|id)?\s*(\d+)", msg)
    if "inspect" in msg and cart_match:
        cart_id = int(cart_match.group(1))
        cart = inspect_cart_by_id(cart_id)
        if cart:
            prods = cart.get("products", [])
            total_qty = sum(p.get("quantity", 1) for p in prods)
            return ChatMessageResponse(
                reply=f"Cart #{cart_id} belongs to User #{cart.get('userId')} and contains {total_qty} items across {len(prods)} product line(s). Date: {cart.get('date', 'Recent')}.",
                tool_used="inspect_cart_by_id",
            )
        return ChatMessageResponse(
            reply=f"Cart #{cart_id} could not be found in active records.",
            tool_used="inspect_cart_by_id",
        )

    # 2. Filter products by category
    # Matches: "electronics", "jewelery", "clothing", "category electronics"
    category_keywords = [
        ("electronic", "electronics"),
        ("jewel", "jewelery"),
        ("men's clothing", "men's clothing"),
        ("women's clothing", "women's clothing"),
        ("clothing", "men's clothing"),
    ]
    matched_cat = None
    for kw, cat in category_keywords:
        if kw in msg:
            matched_cat = cat
            break

    if matched_cat and ("category" in msg or "product" in msg or "filter" in msg or "give" in msg or "list" in msg):
        products = get_products_by_category(matched_cat)
        if products:
            titles = [f"• {p['title']} (${p['price']})" for p in products[:6]]
            summary = "\n".join(titles)
            more = f"\n...and {len(products) - 6} more items." if len(products) > 6 else ""
            return ChatMessageResponse(
                reply=f"Found {len(products)} products in '{matched_cat}':\n\n{summary}{more}",
                tool_used="get_products_by_category",
            )
        return ChatMessageResponse(
            reply=f"No products found in category '{matched_cat}'.",
            tool_used="get_products_by_category",
        )

    # 3. Retrieve all carts
    if "cart" in msg or "basket" in msg or "order" in msg:
        carts = get_all_carts()
        return ChatMessageResponse(
            reply=f"There are currently {len(carts)} customer carts active in the store. You can inspect any specific cart using 'Inspect cart #<id>'.",
            tool_used="get_all_carts",
        )

    # 4. Single product by ID
    prod_id_match = re.search(r"product\s*(?:#|id)?\s*(\d+)", msg)
    if prod_id_match:
        prod_id = int(prod_id_match.group(1))
        prod = get_product(prod_id)
        if prod:
            return ChatMessageResponse(
                reply=f"Product #{prod_id}: {prod.get('title')} — ${prod.get('price')}\nCategory: {prod.get('category')}\nDescription: {prod.get('description')}",
                tool_used="get_product",
            )
        return ChatMessageResponse(
            reply=f"Product #{prod_id} was not found.",
            tool_used="get_product",
        )

    # 5. List all products
    if "product" in msg or "catalog" in msg or "stock" in msg or "items" in msg:
        products = get_all_products()
        if products:
            titles = [f"• #{p['id']} {p['title']} (${p['price']})" for p in products[:5]]
            summary = "\n".join(titles)
            return ChatMessageResponse(
                reply=f"The catalog currently has {len(products)} active SKUs. Here are the top items:\n\n{summary}\n\nYou can ask to filter by category or inspect any item.",
                tool_used="get_all_products",
            )

    # Default fallback
    return ChatMessageResponse(
        reply="I can query our store's products, filter by category (e.g. 'electronics'), inspect customer shopping carts (e.g. 'inspect cart #1'), or list active catalog SKUs. What would you like to see?",
        tool_used=None,
    )
