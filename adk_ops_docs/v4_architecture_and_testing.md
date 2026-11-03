# Milestone 4: Full Architecture & Testing Configuration (`v4_architecture_and_testing.md`)

> ### ⚡ Primary Command
> ```powershell
> pytest -s --env-file dev
> ```
> *(Or quiet single-line summary: `pytest -s -q --env-file dev`)*

This document outlines the complete codebase architecture and evolution in **Milestone 4 (v4)**, introducing **Dynamic Environment Injection for Testing** (`tests/conftest.py`), **Free-Tier Resilient Model Configuration (`gemini-flash-lite-latest`)**, and **Clean Single-Line Output Reporting** (`💚 [Result] ...`).

---

## 1. System Architecture Overview

In Milestone 4, runtime application execution and testing share a unified, environment-aware configuration pipeline:

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
                  │   Default Model: gemini-flash-lite-latest│
                  └────────────────────┬────────────────────┘
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
FastAPI Routers (app/api/)                                     Test Suite (tests/)
        │                                                             │
        ▼                                                             ▼
Service Layer (app/services/)                                  conftest.py
  ├── product_service.py                                       (Hooks, Injection &
  └── cart_service.py                                           Log Cleanliness)
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
│   │   ├── config.py                 # Settings (defaults to gemini-flash-lite-latest)
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
│   └── agent.py                      # Google ADK Agent (model defaults to gemini-flash-lite-latest)
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
│   └── .env.prod                 # Production credentials (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py           # Live Gemini connectivity test
│   │   └── model_list.py             # Live Gemini model list catalog test
│   ├── conftest.py                   # Dynamic pytest --env-file & log suppression hook
│   ├── test_health.py                # Root & health endpoint tests
│   └── test_products.py              # Product schema & service unit tests
├── .gitignore                        # Hardened git ignore
├── PROJECT_DOCUMENTATION.md          # Root project documentation (v4)
├── pytest.ini                        # Pytest configuration with log filtering
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

### Running Tests with Clean Terminal Output (v4)

Run `pytest` specifying the environment file and output flag `-s`:

```powershell
# Run all tests cleanly on dev:
pytest -s -q --env-file dev

# Run all tests cleanly on prod:
pytest -s -q --env-file prod

# Run a specific test suite:
pytest -s tests/agent/api_key_test.py --env-file dev
```

### Clean Terminal Output Example

```text
💚 [Result] Gemini connectivity -> api_key_test.py -> POST /v1beta/models/gemini-flash-lite-latest:generateContent -> returned HTTP 200 with reply: 'Gemini is working!'
💚 [Result] Model catalog -> model_list.py -> GET /v1beta/models -> returned HTTP 200 (10 models available)
💚 [Result] Health endpoint -> test_health.py -> GET /api/v1/health -> returned HTTP 200 with response payload: {'status': 'healthy', 'service': 'business-dashboard'}
💚 [Result] Root endpoint -> test_health.py -> GET / -> returned HTTP 200 with response payload: {'application': 'Business Operations Dashboard', 'version': '1.0.0', 'status': 'running'}
💚 [Result] Schema validation -> test_products.py -> ProductCreate() -> validated payload: title='Valid Product', price=$19.99
💚 [Result] Negative price validation -> test_products.py -> ProductCreate(price=-10.0) -> rejected with ValidationError
💚 [Result] Response serialization -> test_products.py -> ProductResponse() -> serialized ID=42, title='Laptop Stand'
💚 [Result] Service call -> test_products.py -> product_service.get_product(101) -> returned: ID=101, Title='Mock Product'
```

---

## 4. Key Improvements in v4

1. **Free-Tier Model Resilience**:
   - Switched default model from deprecated `gemini-2.5-flash` and high-demand `gemini-3.8-flash` (which throws `503 UNAVAILABLE` during demand spikes) to **`gemini-flash-lite-latest`**, guaranteeing stable `HTTP 200` responses on free tier keys.
2. **Dynamic Environment Ingestion**:
   - `tests/conftest.py` inspects `--env-file dev`, `--env-file prod`, or explicit file paths before importing modules.
3. **Log Noise Suppression**:
   - Muted noisy background ASGI lifecycle and connection logs during tests so terminal output is strictly focused on test results.
4. **Standardized Single-Line Test Signatures**:
   - Every test emits: `💚 [Result] <Topic> -> <script.py> -> <Call/Operation> -> <Outcome>`.
