# Business Operations Dashboard & Google ADK Backend (v5)

A production-ready enterprise backend architecture combining **FastAPI Modular Route Controllers**, **Pydantic Validation Schemas**, a dedicated **Service Layer**, **Google Agent Development Kit (ADK)** with Gemini, an **HTTPX Integration Layer**, and a **Dynamic Environment-Injected Test Suite**.

---

## What's New in v5: Modular API Routing Layer

In **v5**, endpoint definitions are separated from business logic into dedicated route controllers:
- **Modular Route Controllers (`app/api/routes/`)**:
  - `products.py`: Implements `GET /`, `GET /{product_id}`, `GET /category/{category}`, and `POST /` with `ProductCreate` and `ProductResponse` validation.
  - `carts.py`: Implements `GET /` retrieving shopping cart records.
- **Hierarchical Router Aggregation (`app/api/router.py`)**: Sub-routers are mounted cleanly into `api_router` under the `/api/v1` prefix.
- **Route Integration Tests (`tests/test_routes.py`)**: End-to-end tests for all route handlers reporting single-line `💚 [Result]` outputs.
- **Milestone 5 Documentation**: Added `v5_architecture_and_routing.md` and `v5_route_implementation_cookbook.md`.

---

## Architecture Overview

```
Business_ops_GoogleADK/
├── app/                          # Main FastAPI application package
│   ├── api/
│   │   ├── routes/               # [v5] Modular API route controllers
│   │   │   ├── carts.py          # Carts endpoints
│   │   │   └── products.py       # Products CRUD endpoints
│   │   └── router.py             # Versioned API routes registration & aggregator
│   ├── core/
│   │   ├── config.py             # Environment-driven Pydantic settings
│   │   ├── exceptions.py         # Custom application exception hierarchy
│   │   └── logging.py            # Centralized logging configuration
│   ├── integrations/             # External service integration layer
│   │   └── ecommerce_client.py   # HTTPX e-commerce API client & error handler
│   ├── schemas/                  # Request & Response Pydantic models
│   │   └── product.py            # ProductCreate, ProductResponse schemas
│   ├── services/                 # Business domain service layer
│   │   ├── cart_service.py       # Shopping cart operations service
│   │   └── product_service.py    # Product operations service
│   └── main.py                   # FastAPI factory & lifespan setup
├── agenticss/
│   └── agent.py                  # Google ADK Agent definition & tool functions
├── adk_ops_docs/                 # Operational guides & architectural docs
│   ├── git_ssh_authentication_guide.md
│   ├── v1_run_steps.md           # Milestone 1 setup guide
│   ├── v2_calling_an_api.md      # Milestone 2 API integration guide
│   ├── v3_architecture_and_services.md # Milestone 3 architecture guide
│   ├── v3_api_and_schema_cookbook.md   # Milestone 3 schema cookbook
│   ├── v4_architecture_and_testing.md  # Milestone 4 test architecture guide
│   ├── v4_api_and_schema_cookbook.md   # Milestone 4 test cookbook
│   ├── v5_architecture_and_routing.md  # [v5] Milestone 5 architecture & routing guide
│   └── v5_route_implementation_cookbook.md # [v5] Milestone 5 route cookbook
├── environments/
│   ├── .env.example              # Environment template (safe for git)
│   ├── .env.dev                  # Development environment variables (git-ignored)
│   └── .env.prod                 # Production environment variables (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py       # Direct Gemini API connectivity test
│   │   └── model_list.py         # Gemini model catalog inspection test
│   ├── conftest.py               # Dynamic pytest --env-file hook & encoding fix
│   ├── test_health.py            # Health endpoint tests
│   ├── test_products.py          # Product schema & service unit tests
│   └── test_routes.py            # [v5] Route controller integration tests
├── .gitignore                    # Hardened Git ignore configuration
├── PROJECT_DOCUMENTATION.md      # Root project documentation (v5)
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Production and runtime dependencies
└── run.py                        # Multi-environment CLI server runner
```

---

## Steps to Run

### 1. Application Execution

```powershell
# Run development server (loads environments/.env.dev with hot-reload)
python run.py --env dev
```

- Swagger UI: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`
- Products Catalog: `http://localhost:8000/api/v1/products/`
- Shopping Carts: `http://localhost:8000/api/v1/carts/`

### 2. Testing

```powershell
# Run route integration tests:
pytest -s tests/test_routes.py --env-file dev

# Run all tests:
pytest -s -q --env-file dev
```

---

## Security & Git Hygiene

- Real secrets (`environments/.env.dev`, `environments/.env.prod`) are permanently git-ignored.
- Database artifacts (`*.db`, `*.sqlite`, `.adk/`) remain untracked.
- Blank template `environments/.env.example` is maintained for safe onboarding.
