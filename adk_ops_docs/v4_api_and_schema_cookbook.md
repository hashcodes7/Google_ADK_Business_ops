# Milestone 4: API, Schema & Testing Blueprint Cookbook (`v4_api_and_schema_cookbook.md`)

This guide serves as a practical, copy-pasteable reference whenever you want to add a new API endpoint (GET or POST), define strict Pydantic schemas, and write unit/integration tests with dynamic environment file loading.

---

## 1. The 4-Step Development Workflow

Whenever you build a new endpoint or feature in this architecture, you work through 4 modular steps:

```
Step 1: Schema (app/schemas/)      ──> Define Request and Response data models
Step 2: Service (app/services/)    ──> Implement domain business logic
Step 3: Route (app/api/...)        ──> Bind HTTP verb, path, and schemas to route
Step 4: Test (tests/...)           ──> Write unit/integration tests with --env-file
```

---

## 2. Step 1: Defining Strict Schemas (`app/schemas/product.py`)

Separate the **Create/Request payload** from the **Response payload**:

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

Services sit between the API routes and integrations/database. They hold domain logic:

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

Mount the endpoints in your router with strict `response_model` validation:

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

## 5. Step 4: Testing with Dynamic `.env` Injection (`tests/test_products.py`)

In **v4**, tests can dynamically pull credentials from any target environment file.

### Writing the Test

```python
import pytest
from app.schemas.product import ProductCreate, ProductResponse
from app.services import product_service


def test_product_create_schema_validation():
    # Valid payload
    product = ProductCreate(
        title="Valid Product",
        price=19.99,
        description="A high quality product",
        category="electronics",
    )
    assert product.title == "Valid Product"
    assert product.price == 19.99


def test_product_create_invalid_price():
    # Invalid negative price triggers ValidationError
    with pytest.raises(Exception):
        ProductCreate(
            title="Invalid",
            price=-10.0,
            description="desc",
            category="cat",
        )


def test_product_service_mock(monkeypatch):
    sample = {
        "id": 1,
        "title": "Mock Backpack",
        "price": 50.0,
        "description": "Mock desc",
        "category": "bags",
        "image": "",
    }
    from app.integrations.ecommerce_client import ecommerce_client
    monkeypatch.setattr(ecommerce_client, "get_product", lambda pid: sample)

    res = product_service.get_product(1)
    assert res["id"] == 1
    assert res["title"] == "Mock Backpack"
```

### Running the Tests with Target Environments

```powershell
# Run with dev environment:
pytest tests/test_products.py --env-file dev

# Run with production environment:
pytest tests/test_products.py --env-file prod

# Run with custom path:
pytest tests/test_products.py --env-file environments/.env.dev
```

---

## 6. Summary Cheat Sheet for Adding New APIs Later

| Step | Location | What to do |
|---|---|---|
| **1. Define Schema** | `app/schemas/<entity>.py` | Create `<Entity>Create` for request validation and `<Entity>Response` for response serialization. |
| **2. Add Service Method** | `app/services/<entity>_service.py` | Add Python function calling `ecommerce_client` or database. Keep HTTP logic out of here. |
| **3. Mount Endpoint** | `app/api/...` | Use `@router.get` or `@router.post`, specify `response_model=<Entity>Response`, and call the service function. |
| **4. Run Tests** | `tests/test_<entity>.py` | Run `pytest --env-file dev` to verify logic against the target configuration. |
| **5. Check Docs** | `http://localhost:8000/docs` | FastAPI automatically renders the endpoint with full request schemas and response definitions. |
