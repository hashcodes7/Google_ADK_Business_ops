import os
import requests
from google.adk.agents import Agent

# ---------------- CONFIGURATION ----------------


BASE_URL = "https://fakestoreapi.com"


# ---------------- TOOLS ----------------

def get_all_products() -> dict:
    """Get all products from the catalog."""
    response = requests.get(f"{BASE_URL}/products", timeout=10)
    response.raise_for_status()
    return response.json()


def get_product(product_id: int) -> dict:
    """Get a product by its ID."""
    response = requests.get(f"{BASE_URL}/products/{product_id}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_products_by_category(category: str) -> dict:
    """Get products belonging to a category."""
    response = requests.get(
        f"{BASE_URL}/products/category/{category}", timeout=10
    )
    response.raise_for_status()
    return response.json()


def create_product(
    title: str,
    price: float,
    description: str,
    category: str,
    image: str = ""
) -> dict:
    """Create a new product."""
    response = requests.post(
        f"{BASE_URL}/products",
        json={
            "title": title,
            "price": price,
            "description": description,
            "category": category,
            "image": image
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def get_all_carts() -> dict:
    """Get all shopping carts."""
    response = requests.get(f"{BASE_URL}/carts", timeout=10)
    response.raise_for_status()
    return response.json()


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
        get_all_carts
    ]
)
