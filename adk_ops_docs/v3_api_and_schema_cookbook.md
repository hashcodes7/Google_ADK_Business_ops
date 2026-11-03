# Milestone 3: API & Schema Blueprint Cookbook (`v3_api_and_schema_cookbook.md`)

> ### ⚡ Primary Command
> ```powershell
> python -c "from app.schemas.product import ProductCreate; print(ProductCreate(title='Sample', price=29.99, description='Desc', category='clothing'))"
> ```
> *(Or start service to test in Swagger: `python run.py --env dev`)*

This guide serves as a practical, copy-pasteable reference whenever you want to add a new API endpoint (GET or POST) along with strict Pydantic schemas in this project.

---

## 1. The Blueprint: Three Clean Steps to Add Any API

Whenever you build a new endpoint or feature in this architecture, you work through 3 clean files:

```
Step 1: Schema (app/schemas/)      ──> Define Request and Response data models
Step 2: Service (app/services/)    ──> Implement domain business logic
Step 3: Route (app/api/...)        ──> Bind HTTP verb, path, and schemas to route
```

---

## 2. Step 1: Defining Strict Schemas (`app/schemas/product.py`)

Always separate the **Create/Request payload** from the **Response payload**:

```python
from pydantic import BaseModel, Field


# 1. Request Schema: Validates data coming FROM the client
class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Product title")
    price: float = Field(ge=0, description="Price must be non-negative")
    description: str = Field(min_length=1, description="Product description")
    category: str = Field(min_length=1, description="Category name")
    image: str = Field(default="", description="Optional image URL")


# 2. Response Schema: Validates data returned TO the client
# Inherits all fields from ProductCreate and adds the server/db-generated 'id'
class ProductResponse(ProductCreate):
    id: int
```

### Why this design?
- `ProductCreate` ensures clients cannot inject an `id` when creating items.
- Validation happens **before** your route handler code runs. If a client sends `"price": -5`, FastAPI rejects it with HTTP 422 automatically.
- `ProductResponse` guarantees that no private database fields accidentally leak to the client.

---

## 3. Step 2: Implementing the Service Logic (`app/services/product_service.py`)

Services sit between the API routes and integrations/database. They hold business logic:

```python
from app.integrations.ecommerce_client import ecommerce_client


# Logic for GET operations
def get_product(product_id: int):
    """Retrieve a single product by its unique integer identifier."""
    return ecommerce_client.get_product(product_id)


# Logic for POST operations
def create_product(
    title: str,
    price: float,
    description: str,
    category: str,
    image: str = "",
):
    """Create a new product with structured data."""
    product_data = {
        "title": title,
        "price": price,
        "description": description,
        "category": category,
        "image": image,
    }
    return ecommerce_client.create_product(product_data)
```

---

## 4. Step 3: Implementing the REST Endpoints (GET & POST)

Here is how you bind both the **GET** and **POST** APIs to FastAPI using the schemas and service methods above:

```python
from typing import List
from fastapi import APIRouter, status

from app.schemas.product import ProductCreate, ProductResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


# ============================================================================
# GET API PATTERN: Fetch a single resource
# ============================================================================
@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
)
def fetch_product(product_id: int):
    """
    1. FastAPI validates that 'product_id' is an integer.
    2. product_service fetches the data from the integration layer.
    3. 'response_model=ProductResponse' ensures the response strictly conforms 
       to our schema before being returned.
    """
    return product_service.get_product(product_id)


# ============================================================================
# POST API PATTERN: Create a new resource
# ============================================================================
@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def add_product(payload: ProductCreate):
    """
    1. FastAPI parses the incoming JSON against 'ProductCreate'.
    2. If fields are missing or invalid, an automatic 422 error is returned.
    3. Validated payload fields are unpacked into product_service.create_product.
    4. Upstream creates the resource and returns it validated by 'ProductResponse'.
    """
    return product_service.create_product(
        title=payload.title,
        price=payload.price,
        description=payload.description,
        category=payload.category,
        image=payload.image,
    )
```

---

## 5. Summary Cheat Sheet for Adding New APIs Later

| Step | Location | What to do |
|---|---|---|
| **1. Define Schema** | `app/schemas/<entity>.py` | Create `<Entity>Create` for request validation and `<Entity>Response` for response serialization. |
| **2. Add Service Method** | `app/services/<entity>_service.py` | Add Python function calling `ecommerce_client` or database. Keep HTTP logic out of here. |
| **3. Mount Endpoint** | `app/api/...` | Use `@router.get` or `@router.post`, specify `response_model=<Entity>Response`, and call the service function. |
| **4. Check Docs** | `http://localhost:8000/docs` | FastAPI will automatically show the endpoint with full request body schemas and response models! |
