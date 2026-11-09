import os
from google.adk.agents import Agent
from agents.tools.product_tools import (
    get_all_products,
    get_product,
    get_products_by_category,
    create_product,
)
from agents.tools.cart_tools import (
    get_all_carts,
    inspect_cart_by_id,  # Agent-only tool
)
from agents.tools.user_tools import (
    get_all_users,  # Admin-only tool
)

# ---------------- AGENT ----------------

root_agent = Agent(
    name="ecommerce_agent",
    model=os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
    description="An AI assistant for ecommerce operations.",
    instruction="""
    You are an ecommerce operations assistant.

    You can:
    - Retrieve all products.
    - Find products by ID.
    - Filter products by category.
    - Create new products.
    - Retrieve all shopping carts.
    - Inspect a specific cart by ID using `inspect_cart_by_id`.
    - Retrieve all users using `get_all_users` (requires Admin permission).

    Note:
    - Use tools whenever required.
    - Ask for missing details before creating a product.
    - Clearly report tool execution results.
    - If user asks for all users and does not have Admin permission, clearly inform them of the permission denial returned by the tool.
    """,
    tools=[
        get_all_products,
        get_product,
        get_products_by_category,
        create_product,
        get_all_carts,
        inspect_cart_by_id,  # Agent-only capability
        get_all_users,  # Admin-only user listing capability
    ]
)
