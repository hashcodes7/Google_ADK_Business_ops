# Milestone 5: Single Route Implementation Cookbook (`v5_route_implementation_cookbook.md`)

> ### ⚡ Primary Command
> ```powershell
> pytest -s tests/test_routes.py --env-file dev
> ```
> *(Or start server and inspect in Swagger: `python run.py --env dev`)*

This cookbook provides the exact blueprint for implementing a single route function (controller) in this project, showing how to connect HTTP requests, Pydantic schemas, and domain service calls in one modular file.

---

## 1. The Route Controller Pattern

In **v5**, each domain entity has its own dedicated route file under `app/api/routes/<entity>.py`. 

The controller is responsible for:
1. Declaring HTTP verb and URL path.
2. Defining Swagger tags and documentation metadata.
3. Specifying request schema (`ProductCreate`) and response schema (`ProductResponse`).
4. Calling the corresponding domain service method.

---

## 2. Blueprint: Single Route Function Implementation

Here is the exact code pattern used in `app/api/routes/products.py`:

### Example A: Single GET Route with Path Parameter

```python
from fastapi import APIRouter
from app.services import product_service
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    1. 'product_id: int' enforces integer validation on the URL segment.
    2. product_service.get_product(product_id) executes domain logic.
    3. 'response_model=ProductResponse' validates and serializes the outgoing payload.
    """
    return product_service.get_product(product_id)
```

---

### Example B: Single POST Route with Body Validation

```python
from fastapi import APIRouter
from app.services import product_service
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    """
    1. 'product: ProductCreate' parses and validates the incoming JSON body.
    2. product.model_dump() unpacks validated fields into the service layer.
    3. The service delegates creation to the integration client.
    4. Outgoing dict is serialized through ProductResponse.
    """
    return product_service.create_product(**product.model_dump())
```

---

## 3. How to Wire the Route into the Application

Once your route is created in `app/api/routes/<entity>.py`, register it in **`app/api/router.py`**:

```python
from fastapi import APIRouter
from app.api.routes import products, carts  # <-- 1. Import your route module

api_router = APIRouter()

# 2. Include the router
api_router.include_router(products.router)
api_router.include_router(carts.router)


@api_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "business-dashboard"}
```

FastAPI automatically mounts it under `/api/v1/products/` via `app/main.py`.

---

## 4. How to Write a Test for Your Single Route (`tests/test_routes.py`)

Using `TestClient` and `monkeypatch` to test your route in complete isolation:

```python
from fastapi.testclient import TestClient
from app.main import app


def test_get_single_product_route(monkeypatch):
    mock_item = {
        "id": 1,
        "title": "Backpack",
        "price": 49.99,
        "description": "Durable",
        "category": "bags",
        "image": "",
    }
    
    # Mock the service layer:
    from app.services import product_service
    monkeypatch.setattr(product_service, "get_product", lambda pid: mock_item)

    with TestClient(app) as client:
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        print(f"\n💚 [Result] GET /api/v1/products/1 -> routes/products.py -> returned HTTP {response.status_code} for item '{data['title']}'")
```

---

## 5. Summary Checklist for Adding New Routes

| Step | Action | File to Edit |
|---|---|---|
| **1. Define Schema** | Create Request & Response models | `app/schemas/<entity>.py` |
| **2. Add Service** | Implement domain function | `app/services/<entity>_service.py` |
| **3. Create Route File** | Create `APIRouter(prefix="/<entity>")` and endpoint functions | `app/api/routes/<entity>.py` |
| **4. Aggregate Route** | Add `api_router.include_router(<entity>.router)` | `app/api/router.py` |
| **5. Add Integration Test** | Test route with `TestClient` | `tests/test_routes.py` |
| **6. Run & Verify** | Run test command: `pytest -s tests/test_routes.py --env-file dev` | Terminal |
