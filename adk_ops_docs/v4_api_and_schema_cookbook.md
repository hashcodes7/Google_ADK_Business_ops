# Milestone 4: API, Schema & Testing Blueprint Cookbook (`v4_api_and_schema_cookbook.md`)

This guide serves as a practical, copy-pasteable reference whenever you want to add a new API endpoint (GET or POST), define strict Pydantic schemas, and write unit/integration tests with dynamic environment file loading and clean single-line terminal outputs.

---

## 1. The 4-Step Development Workflow

Whenever you build a new endpoint or feature in this architecture, work through 4 clean steps:

```
Step 1: Schema (app/schemas/)      ──> Define Request and Response data models
Step 2: Service (app/services/)    ──> Implement domain business logic
Step 3: Route (app/api/...)        ──> Bind HTTP verb, path, and schemas to route
Step 4: Test (tests/...)           ──> Write unit/integration tests with 💚 single-line output
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

---

## 3. Step 2: Implementing the Service Logic (`app/services/product_service.py`)

Services sit between API routes and integrations/database:

```python
from app.integrations.ecommerce_client import ecommerce_client


# GET operation
def get_product(product_id: int):
    """Retrieve a single product by its unique integer identifier."""
    return ecommerce_client.get_product(product_id)


# POST operation
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

Mount endpoints in your router with strict `response_model` validation:

```python
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
    """Fetch product by ID and serialize via ProductResponse."""
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
    """Validate incoming JSON body via ProductCreate and create product."""
    return product_service.create_product(
        title=payload.title,
        price=payload.price,
        description=payload.description,
        category=payload.category,
        image=payload.image,
    )
```

---

## 5. Step 4: Writing Tests with 💚 Single-Line Output Reporting

Write unit tests that output clean single-line summaries following the project standard:

```python
import pytest
from app.schemas.product import ProductCreate, ProductResponse
from app.services import product_service


def test_product_create_schema_validation():
    product = ProductCreate(
        title="Valid Product",
        price=19.99,
        description="A high quality product",
        category="electronics",
    )
    assert product.title == "Valid Product"
    assert product.price == 19.99
    # Standard output pattern:
    print(f"\n💚 [Result] Schema validation -> test_products.py -> ProductCreate() -> validated payload: title='{product.title}', price=${product.price}")


def test_product_service_mock(monkeypatch):
    sample = {"id": 1, "title": "Backpack", "price": 50.0, "description": "desc", "category": "bags", "image": ""}
    from app.integrations.ecommerce_client import ecommerce_client
    monkeypatch.setattr(ecommerce_client, "get_product", lambda pid: sample)

    res = product_service.get_product(1)
    assert res["id"] == 1
    # Standard output pattern:
    print(f"\n💚 [Result] Service call -> test_products.py -> product_service.get_product(1) -> returned: ID={res['id']}, Title='{res['title']}'")
```

---

## 6. Running Tests

```powershell
# Run with environment injection and clean live output:
pytest -s -q --env-file dev

# Target a single test file:
pytest -s tests/test_products.py --env-file dev
```

---

## 7. Summary Cheat Sheet for Adding New APIs Later

| Step | Location | What to do | Output Pattern |
|---|---|---|---|
| **1. Define Schema** | `app/schemas/<entity>.py` | Create `<Entity>Create` and `<Entity>Response` models. | N/A |
| **2. Add Service Method** | `app/services/<entity>_service.py` | Implement domain function calling client or db. | N/A |
| **3. Mount Endpoint** | `app/api/...` | Use `@router.get` / `@router.post` with `response_model`. | N/A |
| **4. Add Test** | `tests/test_<entity>.py` | Test validations and route/service calls. | `print(f"\n💚 [Result] <Action> -> <file> -> <Call> -> <Outcome>")` |
| **5. Run Pytest** | PowerShell / CLI | `pytest -s -q --env-file dev` | Terminal prints clean 💚 lines |
