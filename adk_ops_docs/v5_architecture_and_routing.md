# Milestone 5: Full Architecture & Routing Layer (`v5_architecture_and_routing.md`)

> ### ⚡ Primary Command
> ```powershell
> python run.py --env dev
> ```
> *(Or run route tests: `pytest -s tests/test_routes.py --env-file dev`)*

This document outlines the complete codebase architecture and evolution in **Milestone 5 (v5)**, introducing modular **FastAPI Route Controllers** (`app/api/routes/`), hierarchical router aggregation in `app/api/router.py`, and complete end-to-end request lifecycle handling.

---

## 1. System Architecture Overview

In Milestone 5, incoming HTTP traffic is cleanly routed through modular controller routers before reaching domain services:

```
Client Request (HTTP GET / POST)
       │
       ▼
app/main.py (FastAPI App, Lifespan & Global Exception Handler)
       │  (prefix: /api/v1)
       ▼
app/api/router.py (Root Aggregator Router)
       ├──> include_router(products.router)  -->  /api/v1/products/...
       ├──> include_router(carts.router)     -->  /api/v1/carts/...
       └──> GET /health                      -->  /api/v1/health
       │
       ▼
Route Handlers (app/api/routes/)
  ├── products.py (GET /, GET /{id}, GET /category/{cat}, POST /)
  └── carts.py (GET /)
       │  (Schema validation via app/schemas/product.py)
       ▼
Service Layer (app/services/)
  ├── product_service.py
  └── cart_service.py
       │
       ▼
Integration Layer (app/integrations/ecommerce_client.py)
       │
       ▼
Upstream Backend (FakeStore API / External E-commerce Backend)
```

---

## 2. Complete Project Directory Layout

```
Business_ops_GoogleADK/
├── app/
│   ├── api/
│   │   ├── routes/                   # [v5] Modular API route controllers
│   │   │   ├── carts.py              # Shopping cart HTTP endpoints
│   │   │   └── products.py           # Product catalog CRUD endpoints
│   │   └── router.py                 # Central aggregator router
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings & environment config
│   │   ├── exceptions.py             # Custom application exception hierarchy
│   │   └── logging.py                # Logging configuration & formatting
│   ├── integrations/
│   │   └── ecommerce_client.py       # Upstream HTTPX client & error mapping
│   ├── schemas/                      # Pydantic validation models
│   │   └── product.py                # ProductCreate and ProductResponse schemas
│   ├── services/                     # Business domain service layer
│   │   ├── cart_service.py           # Shopping cart operations service
│   │   └── product_service.py        # Product operations service
│   └── main.py                       # FastAPI factory, lifespan & root endpoints
├── agenticss/
│   └── agent.py                      # Google ADK agent with tool bindings
├── adk_ops_docs/
│   ├── git_ssh_authentication_guide.md
│   ├── v1_run_steps.md               # v1 execution guide
│   ├── v2_calling_an_api.md          # v2 API integration guide
│   ├── v3_architecture_and_services.md # v3 architecture guide
│   ├── v3_api_and_schema_cookbook.md # v3 GET/POST schema cookbook
│   ├── v4_architecture_and_testing.md # v4 testing architecture guide
│   ├── v4_api_and_schema_cookbook.md # v4 testing cookbook
│   ├── v5_architecture_and_routing.md # [v5] Full architecture & routing guide (this file)
│   └── v5_route_implementation_cookbook.md # [v5] Single route implementation cookbook
├── environments/
│   ├── .env.example                  # Template configuration (safe for git)
│   ├── .env.dev                      # Local dev credentials (git-ignored)
│   └── .env.prod                     # Production credentials (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py           # Live Gemini connectivity test
│   │   └── model_list.py             # Gemini model list test
│   ├── conftest.py                   # Dynamic pytest --env-file & encoding hook
│   ├── test_health.py                # Health & root endpoint tests
│   ├── test_products.py              # Product schema & service unit tests
│   └── test_routes.py                # [v5] Route controller integration tests
├── .gitignore                        # Hardened git ignore
├── PROJECT_DOCUMENTATION.md          # Root project documentation (v5)
├── pytest.ini                        # Pytest configuration
├── requirements.txt                  # Dependency list
└── run.py                            # Multi-environment CLI server launcher
```

---

## 3. Steps to Run & Verify v5 Routes

### 1. Launch the Server

```powershell
python run.py --env dev
```

- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Spec**: `http://localhost:8000/redoc`

### 2. Available v5 Endpoints

| Method | Path | Description | Response Model |
|---|---|---|---|
| `GET` | `/` | Root running status | `{"application": ..., "version": ..., "status": ...}` |
| `GET` | `/api/v1/health` | Service health status | `{"status": "healthy", "service": ...}` |
| `GET` | `/api/v1/products/` | List all products | `list[ProductResponse]` |
| `GET` | `/api/v1/products/{product_id}` | Get product by ID | `ProductResponse` |
| `GET` | `/api/v1/products/category/{category}` | Filter products by category | `list[ProductResponse]` |
| `POST` | `/api/v1/products/` | Create a new product | `ProductResponse` |
| `GET` | `/api/v1/carts/` | List all carts | `list[dict]` |

### 3. Run Route Integration Tests

```powershell
pytest -s tests/test_routes.py --env-file dev
```

Clean single-line output:
```text
💚 [Result] GET /api/v1/products/ -> routes/products.py -> returned HTTP 200 with 1 items
💚 [Result] GET /api/v1/products/1 -> routes/products.py -> returned HTTP 200 for item 'Backpack'
💚 [Result] POST /api/v1/products/ -> routes/products.py -> returned HTTP 200 created ID=99
💚 [Result] GET /api/v1/carts/ -> routes/carts.py -> returned HTTP 200 with 1 carts
```

---

## 4. Comprehensive File, Class, and Method Reference

### A. Route Controllers (`app/api/routes/`)

#### `app/api/routes/products.py`
- **`router`**: `APIRouter(prefix="/products", tags=["Products"])`
- **Endpoints**:
  - `get_products() -> list[ProductResponse]`:
    - Method: `GET /`
    - Calls: `product_service.get_all_products()`
    - Serializes output against `list[ProductResponse]`.
  - `get_product(product_id: int) -> ProductResponse`:
    - Method: `GET /{product_id}`
    - Parameter: Integer path parameter `product_id`.
    - Calls: `product_service.get_product(product_id)`
    - Automatically maps missing items to `404 Not Found`.
  - `get_products_by_category(category: str) -> list[ProductResponse]`:
    - Method: `GET /category/{category}`
    - Calls: `product_service.get_products_by_category(category)`.
  - `create_product(product: ProductCreate) -> ProductResponse`:
    - Method: `POST /`
    - Validates incoming body with `ProductCreate`.
    - Unpacks validated fields: `product_service.create_product(**product.model_dump())`.
    - Returns `ProductResponse` with generated ID.

#### `app/api/routes/carts.py`
- **`router`**: `APIRouter(prefix="/carts", tags=["Carts"])`
- **Endpoints**:
  - `get_carts()`:
    - Method: `GET /`
    - Calls: `cart_service.get_all_carts()`
    - Returns raw list of shopping carts.

#### `app/api/router.py` (Central Aggregator)
- Imports `products.router` and `carts.router`.
- Includes them using `api_router.include_router(...)`.
- Exposes GET `/health` for load balancers.
