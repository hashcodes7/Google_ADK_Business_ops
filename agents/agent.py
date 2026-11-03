import os
from google.adk.agents import Agent
from agents.tools.product_tools import (
    get_all_products,
    get_product,
    get_products_by_category,
    create_product,
)
from agents.tools.cart_tools import get_all_carts

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
    - Retrieve shopping carts.

    Use tools whenever required.
    Ask for missing product details before creating a product.
    Clearly report tool execution results.
    """,
    tools=[
        get_all_products,
        get_product,
        get_products_by_category,
        create_product,
        get_all_carts,
    ]
)
