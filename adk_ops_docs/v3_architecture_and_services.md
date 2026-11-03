# Milestone 3: Full Architecture & Services Layer (`v3_architecture_and_services.md`)

> ### ⚡ Primary Command
> ```powershell
> python run.py --env dev
> ```
> *(Starts FastAPI with hot-reload, loading `environments/.env.dev` for schema validation & service layers)*

This document outlines the complete codebase architecture and evolution in **Milestone 3 (v3)**, introducing the **Service Layer** (`app/services/`) and **Schema Validation Layer** (`app/schemas/`) alongside the integration layer and FastAPI core.

---

## 1. System Architecture Overview

With Milestone 3, the project follows a layered architectural pattern:

```
FastAPI Router (app/api/)
       │
       ▼
Service Layer (app/services/)  <───> Schema Layer (app/schemas/)
       │                              (Strict Pydantic request & response models)
       ▼
Integration Layer (app/integrations/)
       │
       ▼
Upstream Backend (FakeStore API / E-commerce Backend)
```

### Complete Project Layout

```
Business_ops_GoogleADK/
├── app/
│   ├── api/
│   │   └── router.py                 # Core API route registration & health checks
│   ├── core/
│   │   ├── config.py                 # Pydantic Settings & environment variables
│   │   ├── exceptions.py             # Custom application exception hierarchy
│   │   └── logging.py                # Standardized system logging configuration
│   ├── integrations/
│   │   └── ecommerce_client.py       # HTTPX client for remote API calls
│   ├── schemas/                      # [v3] Request/Response Pydantic Models
│   │   └── product.py                # ProductCreate and ProductResponse schemas
│   ├── services/                     # [v3] Business & Domain Service Layer
│   │   ├── cart_service.py           # Shopping cart domain service
│   │   └── product_service.py        # Product operations domain service
│   └── main.py                       # FastAPI factory, exception handlers & lifespan
├── agenticss/
│   └── agent.py                      # Google ADK Agent & LLM tool definitions
├── adk_ops_docs/
│   ├── git_ssh_authentication_guide.md
│   ├── v1_run_steps.md               # v1 execution guide
│   ├── v2_calling_an_api.md          # v2 API integration guide
│   ├── v3_architecture_and_services.md # v3 full codebase reference (this file)
│   └── v3_api_and_schema_cookbook.md # v3 GET/POST & schema blueprint cookbook
├── environments/
│   ├── .env.example                  # Template configuration (safe for git)
│   ├── .env.dev                      # Local dev credentials (git-ignored)
│   └── .env.prod                     # Production credentials (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py           # Gemini direct key verification
│   │   └── model_list.py             # Gemini model list verification
│   ├── test_health.py                # Health endpoint tests
│   └── test_products.py              # Product endpoint tests
├── .gitignore                        # Hardened git ignore
├── PROJECT_DOCUMENTATION.md          # Root project documentation (v3)
├── pytest.ini                        # Pytest settings
├── requirements.txt                  # Dependency list
└── run.py                            # Multi-environment CLI server launcher
```

---

## 2. Steps to Run the Project

### Prerequisites
- Python 3.11 or 3.12
- Active virtual environment (`.venv`)

### Installation & Execution

```powershell
# 1. Activate Virtual Environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Start development server (loads environments/.env.dev with hot-reload)
python run.py --env dev

# Or start in production mode (loads environments/.env.prod)
python run.py --env prod
```

- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Endpoint**: `http://localhost:8000/api/v1/health`

---

## 3. Comprehensive File, Class, and Method Reference

### A. Schemas Layer (`app/schemas/`)

Strict Pydantic data models enforcing validation on both incoming request bodies and outgoing responses.

#### `app/schemas/product.py`
- **Classes**:
  - `ProductCreate(BaseModel)`:
    - *Purpose*: Defines and validates the payload when creating a new product.
    - *Fields*:
      - `title: str = Field(min_length=1, max_length=200)`: Product title (non-empty, max 200 chars).
      - `price: float = Field(ge=0)`: Product price (must be greater than or equal to 0).
      - `description: str = Field(min_length=1)`: Product description text.
      - `category: str = Field(min_length=1)`: Product category.
      - `image: str = ""`: Product image URL (optional, defaults to empty string).
  - `ProductResponse(ProductCreate)`:
    - *Purpose*: Inherits all attributes of `ProductCreate` and adds database/upstream identifiers for API responses.
    - *Fields*:
      - `id: int`: Unique identifier assigned by the database or upstream system.

---

### B. Service Layer (`app/services/`)

Decouples business logic from HTTP endpoints and database/integration clients.

#### `app/services/product_service.py`
- **Functions**:
  - `get_all_products()`:
    - *Description*: Retrieves all products from the catalog.
    - *Calls*: `ecommerce_client.get_all_products()`.
    - *Returns*: List of raw product dictionaries.
  - `get_product(product_id: int)`:
    - *Description*: Retrieves a single product by its unique integer identifier.
    - *Calls*: `ecommerce_client.get_product(product_id)`.
    - *Returns*: Single product dictionary.
  - `get_products_by_category(category: str)`:
    - *Description*: Queries products belonging to a specified category.
    - *Calls*: `ecommerce_client.get_products_by_category(category)`.
    - *Returns*: Filtered list of product dictionaries.
  - `create_product(title: str, price: float, description: str, category: str, image: str = "")`:
    - *Description*: Formats incoming product attributes into a structured dictionary and sends it to the upstream service.
    - *Calls*: `ecommerce_client.create_product(product_data)`.
    - *Returns*: Created product dictionary with assigned ID.

#### `app/services/cart_service.py`
- **Functions**:
  - `get_all_carts()`:
    - *Description*: Retrieves all customer shopping cart records.
    - *Calls*: `ecommerce_client.get_all_carts()`.
    - *Returns*: List of shopping cart records.

---

### C. Integration Layer (`app/integrations/`)

#### `app/integrations/ecommerce_client.py`
- **Classes**:
  - `EcommerceClient`:
    - `__init__(self)`: Loads `settings.ECOMMERCE_API_URL` and establishes a 10.0s HTTP timeout.
    - `_request(self, method: str, endpoint: str, **kwargs)`: Sends HTTP requests via scoped `httpx.Client()`. Catches `HTTPStatusError` (maps 404 to `ResourceNotFoundException`, others to `ExternalAPIException`) and `RequestError` (maps to `ExternalAPIException`).
    - `get_all_products(self)`: Dispatches `GET /products`.
    - `get_product(self, product_id: int)`: Dispatches `GET /products/{product_id}`.
    - `get_products_by_category(self, category: str)`: Sanitizes category with `urllib.parse.quote` and calls `GET /products/category/{category}`.
    - `create_product(self, product_data: dict)`: Dispatches `POST /products` with JSON payload.
    - `get_all_carts(self)`: Dispatches `GET /carts`.
- **Singletons**:
  - `ecommerce_client`: Pre-instantiated singleton for project-wide use.

---

### D. Core & Application Configuration (`app/core/` and `app/main.py`)

- **`app/core/config.py`**:
  - `Settings(BaseSettings)`: Pydantic settings loading `APP_NAME`, `APP_VERSION`, `DEBUG`, `API_V1_PREFIX`, `ECOMMERCE_API_URL`, `GOOGLE_API_KEY`, `LOG_LEVEL`.
  - `get_settings()`: Cached configuration provider.
- **`app/core/exceptions.py`**:
  - `ApplicationException`: Base error class (status code 500).
  - `ExternalAPIException`: Upstream failure (status code 502).
  - `ResourceNotFoundException`: Missing item (status code 404).
  - `ValidationException`: Invalid client input (status code 400).
- **`app/core/logging.py`**:
  - `setup_logging(level)`: Configures stdout stream formatting.
- **`app/main.py`**:
  - `lifespan(app)`: Context manager logging startup and shutdown.
  - `application_exception_handler(request, exc)`: Global exception handler formatting standard error JSON.
  - `root()`: Health and version check at `/`.
- **`run.py`**:
  - Command-line runner (`--env dev|prod`) dynamically activating environment files before running Uvicorn.
