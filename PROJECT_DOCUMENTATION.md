# Business Operations Dashboard & Google ADK Backend (v3)

A production-ready enterprise backend architecture combining **FastAPI**, **Pydantic Validation Schemas**, a dedicated **Service Layer**, **Google Agent Development Kit (ADK)** with Gemini 2.5 Flash, and an **HTTPX Integration Layer** for upstream e-commerce services.

---

## What's New in v3: Services & Schema Validation Layers

In **v3**, the backend introduces strict API schema validation and a domain service layer:
- **Strict Pydantic Schemas (`app/schemas/`)**: Decouples incoming request bodies (`ProductCreate`) from outgoing serialized responses (`ProductResponse`), enforcing bounds on fields (e.g. `price >= 0`, title character limits).
- **Domain Service Layer (`app/services/`)**: Separates endpoint handling from client networking (`product_service.py`, `cart_service.py`).
- **Standardized Cookbook (`adk_ops_docs/`)**: Added blueprint guides for building GET/POST endpoints with strict schema definitions.

---

## Architecture Overview

```
Business_ops_GoogleADK/
├── app/                          # Main FastAPI application package
│   ├── api/
│   │   └── router.py             # Versioned API routes registration
│   ├── core/
│   │   ├── config.py             # Environment-driven Pydantic settings
│   │   ├── exceptions.py         # Custom application exception hierarchy
│   │   └── logging.py            # Centralized logging configuration
│   ├── integrations/             # External service integration layer
│   │   └── ecommerce_client.py   # HTTPX e-commerce API client & error handler
│   ├── schemas/                  # [v3] Request & Response Pydantic models
│   │   └── product.py            # ProductCreate, ProductResponse schemas
│   ├── services/                 # [v3] Business domain service layer
│   │   ├── cart_service.py       # Shopping cart operations service
│   │   └── product_service.py    # Product operations service
│   └── main.py                   # FastAPI factory & lifespan setup
├── agenticss/
│   └── agent.py                  # Google ADK Agent definition & tool functions
├── adk_ops_docs/                 # Operational guides & architectural docs
│   ├── git_ssh_authentication_guide.md
│   ├── v1_run_steps.md           # Milestone 1 setup guide
│   ├── v2_calling_an_api.md      # Milestone 2 API integration guide
│   ├── v3_architecture_and_services.md # Milestone 3 full architecture guide
│   └── v3_api_and_schema_cookbook.md   # Milestone 3 GET/POST schema cookbook
├── environments/
│   ├── .env.example              # Environment template (safe for git)
│   ├── .env.dev                  # Development environment variables (git-ignored)
│   └── .env.prod                 # Production environment variables (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py       # Direct Gemini API connectivity test
│   │   └── model_list.py         # Gemini model catalog inspection test
│   ├── test_health.py            # Health endpoint tests
│   └── test_products.py          # Product endpoint tests
├── .gitignore                    # Hardened Git ignore configuration
├── PROJECT_DOCUMENTATION.md      # Root project documentation
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Production and runtime dependencies
└── run.py                        # Multi-environment CLI server runner
```

---

## Steps to Run

### 1. Environment Setup

```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies if needed
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Verify `environments/.env.dev` has the required configuration:

```ini
APP_ENV=dev
APP_NAME="Business Operations Dashboard"
APP_VERSION=1.0.0
DEBUG=true
API_V1_PREFIX=/api/v1
ECOMMERCE_API_URL=https://fakestoreapi.com
GOOGLE_API_KEY=your_gemini_api_key_here
LOG_LEVEL=INFO
```

### 3. Run the Application

```powershell
# Development mode with hot-reload
python run.py --env dev

# Production mode
python run.py --env prod
```

- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

---

## Detailed File, Class, and Method Reference

### 1. Schema Validation Layer: `app/schemas/product.py` *(New in v3)*
- **Classes**:
  - `ProductCreate(BaseModel)`:
    - `title: str = Field(min_length=1, max_length=200)`
    - `price: float = Field(ge=0)`
    - `description: str = Field(min_length=1)`
    - `category: str = Field(min_length=1)`
    - `image: str = ""`
  - `ProductResponse(ProductCreate)`:
    - `id: int`: Adds database/upstream ID for response serialization.

---

### 2. Service Layer: `app/services/` *(New in v3)*

#### `app/services/product_service.py`
- `get_all_products()`: Calls `ecommerce_client.get_all_products()`.
- `get_product(product_id: int)`: Calls `ecommerce_client.get_product(product_id)`.
- `get_products_by_category(category: str)`: Calls `ecommerce_client.get_products_by_category(category)`.
- `create_product(title, price, description, category, image="")`: Calls `ecommerce_client.create_product(product_data)`.

#### `app/services/cart_service.py`
- `get_all_carts()`: Calls `ecommerce_client.get_all_carts()`.

---

### 3. Integration Layer: `app/integrations/ecommerce_client.py`
- `EcommerceClient`: Context-managed `httpx.Client()` calls with 10.0s timeout, error logging, and translation into `ResourceNotFoundException` (404) or `ExternalAPIException` (5xx/connection failure).
- Singleton: `ecommerce_client`.

---

### 4. Application Core & Entrypoint
- `app/core/config.py`: `Settings` with Pydantic BaseSettings and `get_settings()`.
- `app/core/exceptions.py`: `ApplicationException`, `ExternalAPIException`, `ResourceNotFoundException`, `ValidationException`.
- `app/core/logging.py`: Centralized `setup_logging()`.
- `app/main.py`: FastAPI application lifespan, custom exception handler, `/` root route.
- `run.py`: Multi-environment `--env` runner.
