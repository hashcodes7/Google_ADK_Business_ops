# Business Operations Dashboard & Google ADK Backend (v4)

A production-ready enterprise backend architecture combining **FastAPI**, **Pydantic Validation Schemas**, a dedicated **Service Layer**, **Google Agent Development Kit (ADK)** with Gemini, an **HTTPX Integration Layer**, and a **Dynamic Environment-Injected Test Suite**.

---

## What's New in v4: Dynamic Test Environment Injection

In **v4**, the testing framework is enhanced with dynamic configuration loading:
- **`pytest --env-file` CLI Hook (`tests/conftest.py`)**: Enables developers and CI/CD pipelines to run test suites against specific environments (e.g., `pytest --env-file dev` or `pytest --env-file prod`).
- **Pre-Collection Variable Normalization**: Synchronizes environment aliases (`Gemini_API_KEY` $\leftrightarrow$ `GOOGLE_API_KEY`, `ECOMMERCE_API_BASE_URL` $\leftrightarrow$ `ECOMMERCE_API_URL`) before modules are loaded.
- **Updated Test Suite**: Aligned health and schema unit tests with the refactored `app/` architecture.
- **Comprehensive Documentation**: Added `v4_architecture_and_testing.md` and `v4_api_and_schema_cookbook.md`.

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
│   ├── v4_architecture_and_testing.md  # [v4] Milestone 4 architecture & test guide
│   └── v4_api_and_schema_cookbook.md   # [v4] Milestone 4 cookbook & test guide
├── environments/
│   ├── .env.example              # Environment template (safe for git)
│   ├── .env.dev                  # Development environment variables (git-ignored)
│   └── .env.prod                 # Production environment variables (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py       # Direct Gemini API connectivity test
│   │   └── model_list.py         # Gemini model catalog inspection test
│   ├── conftest.py               # [v4] Dynamic pytest --env-file hook
│   ├── test_health.py            # Health endpoint tests
│   └── test_products.py          # Product schema & service unit tests
├── .gitignore                    # Hardened Git ignore configuration
├── PROJECT_DOCUMENTATION.md      # Root project documentation (v4)
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Production and runtime dependencies
└── run.py                        # Multi-environment CLI server runner
```

---

## Steps to Run

### 1. Application Execution

```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Run development server (loads environments/.env.dev with hot-reload)
python run.py --env dev

# Run production server
python run.py --env prod
```

### 2. Running Tests with Dynamic Environment Selection

```powershell
# Run with development credentials
pytest --env-file dev

# Run with production credentials
pytest --env-file prod

# Run unit tests specifically
pytest tests/test_products.py --env-file dev
```

---

## Security & Git Hygiene

- Real secrets (`environments/.env.dev`, `environments/.env.prod`) are permanently git-ignored.
- Database artifacts (`*.db`, `*.sqlite`, `.adk/`) remain untracked.
- Blank template `environments/.env.example` is maintained for safe onboarding.
