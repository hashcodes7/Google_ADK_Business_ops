# Milestone 4: Full Architecture & Testing Configuration (`v4_architecture_and_testing.md`)

This document outlines the complete codebase architecture and evolution in **Milestone 4 (v4)**, introducing **Dynamic Environment Injection for Testing** (`tests/conftest.py`) alongside the Service Layer, Schemas Layer, and Integration Layer.

---

## 1. System Architecture Overview

With Milestone 4, the test harness and application runtime share a unified, environment-aware configuration pipeline:

```
                  ┌─────────────────────────────────────────┐
                  │ Runtime Launcher (run.py --env dev/prod)│
                  │ OR Pytest Runner (pytest --env-file ...)│
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │   Environment (.env.dev / .env.prod)    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │   Pydantic Settings (app/core/config)   │
                  └────────────────────┬────────────────────┘
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
FastAPI Routers (app/api/)                                     Test Suite (tests/)
        │                                                             │
        ▼                                                             ▼
Service Layer (app/services/)                                  conftest.py
  ├── product_service.py                                       (Hooks & Injection)
  └── cart_service.py
        │
        ▼
Schemas Layer (app/schemas/)
  └── product.py (Pydantic Models)
        │
        ▼
Integration Layer (app/integrations/)
  └── ecommerce_client.py (HTTPX client)
        │
        ▼
Upstream Services (E-commerce Backend / FakeStore API)
```

---

## 2. Complete Project Directory Layout

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
│   ├── schemas/                      # Request/Response Pydantic Models
│   │   └── product.py                # ProductCreate and ProductResponse schemas
│   ├── services/                     # Business & Domain Service Layer
│   │   ├── cart_service.py           # Shopping cart domain service
│   │   └── product_service.py        # Product operations domain service
│   └── main.py                       # FastAPI factory, exception handlers & lifespan
├── agenticss/
│   └── agent.py                      # Google ADK Agent & LLM tool definitions
├── adk_ops_docs/
│   ├── git_ssh_authentication_guide.md
│   ├── v1_run_steps.md               # v1 execution guide
│   ├── v2_calling_an_api.md          # v2 API integration guide
│   ├── v3_architecture_and_services.md # v3 architecture guide
│   ├── v3_api_and_schema_cookbook.md # v3 GET/POST & schema blueprint cookbook
│   ├── v4_architecture_and_testing.md # v4 full architecture & test guide (this file)
│   └── v4_api_and_schema_cookbook.md # v4 cookbook with testing & schema workflows
├── environments/
│   ├── .env.example                  # Template configuration (safe for git)
│   ├── .env.dev                      # Local dev credentials (git-ignored)
│   └── .env.prod                     # Production credentials (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py           # Gemini key connectivity verification test
│   │   └── model_list.py             # Gemini model list verification test
│   ├── conftest.py                   # [v4] Dynamic pytest --env-file hook
│   ├── test_health.py                # Root & health endpoint tests
│   └── test_products.py              # Product schema & service unit tests
├── .gitignore                        # Hardened git ignore
├── PROJECT_DOCUMENTATION.md          # Root project documentation (v4)
├── pytest.ini                        # Pytest configuration
├── requirements.txt                  # Dependency list
└── run.py                            # Multi-environment CLI server launcher
```

---

## 3. Steps to Run the Project & Test Suite

### Running the Application

```powershell
# 1. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 2. Start server in development mode (loads environments/.env.dev)
python run.py --env dev

# 3. Start server in production mode (loads environments/.env.prod)
python run.py --env prod
```

### Running Tests with Dynamic Environment Injection (v4)

You can now explicitly point `pytest` to any environment file or shortcut:

```powershell
# Run tests with dev environment credentials:
pytest --env-file dev

# Run tests with production credentials:
pytest --env-file prod

# Run tests with an explicit file path:
pytest --env-file environments/.env.dev

# Or use environment variables:
$env:ENV_FILE="environments/.env.dev"; pytest
```

---

## 4. Comprehensive File, Class, and Method Reference

### A. Testing & Environment Injection (`tests/conftest.py`) *(New in v4)*

- **Functions**:
  - `pytest_addoption(parser)`:
    - Registers the custom CLI flag `--env-file` for `pytest`.
  - `pytest_configure(config)`:
    - Executed by pytest before any test module is imported or collected.
    - Resolves the requested environment file (supporting shortcuts `'dev'`, `'prod'`, `'example'`, or direct paths).
    - Injects the environment variables using `load_dotenv(dotenv_path, override=True)`.
    - Normalizes alias environment variables (e.g., synchronizing `Gemini_API_KEY` $\leftrightarrow$ `GOOGLE_API_KEY`, and `ECOMMERCE_API_BASE_URL` $\leftrightarrow$ `ECOMMERCE_API_URL`).

---

### B. Schemas Layer (`app/schemas/product.py`)

- **Classes**:
  - `ProductCreate(BaseModel)`: Request payload schema.
    - `title: str = Field(min_length=1, max_length=200)`
    - `price: float = Field(ge=0)`
    - `description: str = Field(min_length=1)`
    - `category: str = Field(min_length=1)`
    - `image: str = ""`
  - `ProductResponse(ProductCreate)`: Response payload schema inheriting all fields from `ProductCreate` plus:
    - `id: int`: Server/database assigned identifier.

---

### C. Service Layer (`app/services/`)

- **`app/services/product_service.py`**:
  - `get_all_products()`: Calls `ecommerce_client.get_all_products()`.
  - `get_product(product_id: int)`: Calls `ecommerce_client.get_product(product_id)`.
  - `get_products_by_category(category: str)`: Calls `ecommerce_client.get_products_by_category(category)`.
  - `create_product(title, price, description, category, image="")`: Formats payload and calls `ecommerce_client.create_product(product_data)`.
- **`app/services/cart_service.py`**:
  - `get_all_carts()`: Calls `ecommerce_client.get_all_carts()`.

---

### D. Integration Layer (`app/integrations/ecommerce_client.py`)

- **`EcommerceClient`**:
  - `__init__(self)`: Initializes base URL from `settings.ECOMMERCE_API_URL` and sets 10.0s timeout.
  - `_request(self, method: str, endpoint: str, **kwargs)`: Dispatches HTTP request via `httpx.Client()`. Handles `httpx.HTTPStatusError` (maps 404 to `ResourceNotFoundException`, others to `ExternalAPIException`) and `httpx.RequestError` (maps to `ExternalAPIException`).
  - `get_all_products(self)`: `GET /products`.
  - `get_product(self, product_id: int)`: `GET /products/{product_id}`.
  - `get_products_by_category(self, category: str)`: `GET /products/category/{category}` with URL escaping.
  - `create_product(self, product_data: dict)`: `POST /products`.
  - `get_all_carts(self)`: `GET /carts`.
- **Singleton**: `ecommerce_client`.

---

### E. Core Configuration & Server

- **`app/core/config.py`**: `Settings` Pydantic class and `get_settings()` singleton.
- **`app/core/exceptions.py`**: `ApplicationException`, `ExternalAPIException`, `ResourceNotFoundException`, `ValidationException`.
- **`app/core/logging.py`**: `setup_logging()`.
- **`app/main.py`**: FastAPI app, lifespan context manager, root health endpoint, and global exception handler.
- **`run.py`**: CLI environment parser (`--env dev|prod`) and Uvicorn launcher.
