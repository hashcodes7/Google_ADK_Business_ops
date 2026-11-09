# Business Operations Dashboard & Google ADK Backend (v7)

A production-ready enterprise backend architecture combining **Hexagonal Architecture (Ports & Adapters)**, **Hot-Swappable Bearer Authentication**, **Role-Based Access Control (RBAC)**, **User vs Agent Channel Isolation**, **FastAPI Modular Route Controllers**, **Pydantic Schemas**, a dedicated **Service Layer**, **Google Agent Development Kit (ADK)** with Gemini (`gemini-flash-lite-latest`), an **HTTPX Integration Layer**, and a **Dynamic Environment-Injected Test Suite**.

---

## What's New in v7: Hexagonal Architecture, Modular Auth & Channel Isolation

In **v7**, the system implements clean domain segregation, plug-and-play authentication, and explicit operational channel barriers:
- **Hot-Swappable Auth Adapter (`app/core/auth.py`)**: All HTTP Bearer token parsing and identity resolution is centralized in a single file for zero-friction swapping to OAuth2/JWT without impacting services or routes.
- **SecurityContext & Role-Based Access Control (`app/core/security.py`)**:
  - `SecurityContext(user_id, role, actor)` carries caller identity, role (`Business` vs `Admin`), and caller origin (`human` vs `agent`).
  - `require_permission(context, permission)` enforces domain permissions directly in shared application services.
- **Channel Isolation & Segregation**:
  - **User-Only Channel**: `POST /api/v1/users/` (Admin user provisioning) is exposed strictly via REST and withheld from LLM tools.
  - **Agent-Only Channel**: `inspect_cart_by_id(cart_id)` is exposed strictly as a Google ADK tool for LLM operational analysis.
  - **Shared Channels**: Catalog browsing/creation and cart listing are accessible to both human operators and autonomous agents.
- **Hexagonal Ports & Driven Adapters (`app/ports/`, `app/integrations/`)**: Pure protocol definitions decoupled from external HTTP client details.
- **Milestone 7 Documentation**:
  - `adk_ops_docs/v7_hexagonal_auth_and_channels.md`
  - `adk_ops_docs/v7_tools_and_api_guide.md`

---

## Architecture Overview

```
Business_ops_GoogleADK/
├── app/                          # Main FastAPI application package
│   ├── api/
│   │   ├── routes/               # Modular API route controllers
│   │   │   ├── carts.py          # GET /api/v1/carts/
│   │   │   ├── products.py       # GET, POST /api/v1/products/
│   │   │   └── users.py          # [User-Only] POST /api/v1/users/ (Admin)
│   │   └── router.py             # Route aggregator
│   ├── core/
│   │   ├── auth.py               # [v7] Hot-swappable Auth Adapter & Dependency
│   │   ├── security.py           # [v7] SecurityContext, Roles & require_permission
│   │   ├── config.py             # Environment settings (Gemini, FakeStore)
│   │   ├── exceptions.py         # Custom application exceptions (401, 403, 404, 502)
│   │   └── logging.py            # Centralized logging configuration
│   ├── ports/                    # [v7] Hexagonal Outbound Ports
│   │   └── ecommerce_port.py     # Protocol for downstream commerce integrations
│   ├── integrations/             # Outbound Driven Adapters
│   │   └── ecommerce_client.py   # HTTPX client implementing ecommerce_port
│   ├── schemas/                  # Request & Response Pydantic models
│   │   ├── product.py            # ProductCreate, ProductResponse schemas
│   │   └── user.py               # [v7] UserCreate, UserResponse schemas
│   ├── services/                 # Shared domain business services
│   │   ├── cart_service.py       # Shopping cart service (RBAC checked)
│   │   ├── product_service.py    # Product operations service (RBAC checked)
│   │   └── user_service.py       # [v7] User provisioning service (RBAC checked)
│   └── main.py                   # FastAPI application factory & lifespan setup
├── agents/                       # Google ADK Inbound Adapter
│   ├── agent.py                  # Agent orchestrator (gemini-flash-lite-latest)
│   └── tools/
│       ├── cart_tools.py         # Carts tools + [Agent-Only] inspect_cart_by_id
│       └── product_tools.py      # Product catalog tools
├── adk_ops_docs/                 # Versioned Milestone Guides
│   ├── v1_run_steps.md           # Milestone 1: Setup & execution
│   ├── v2_calling_an_api.md      # Milestone 2: API integrations
│   ├── v3_architecture_and_services.md # Milestone 3: Services layer
│   ├── v4_architecture_and_testing.md  # Milestone 4: Test architecture
│   ├── v5_architecture_and_routing.md  # Milestone 5: Modular routing
│   ├── v6_hexagonal_architecture.md    # Milestone 6: Initial hexagonal model
│   ├── v7_hexagonal_auth_and_channels.md # [v7] Auth & channel isolation
│   └── v7_tools_and_api_guide.md       # [v7] API & tools access cookbook
├── environments/
│   ├── .env.example              # Environment template
│   ├── .env.dev                  # Development settings (git-ignored)
│   └── .env.prod                 # Production settings (git-ignored)
├── tests/
│   ├── test_hexagonal_architecture.py # [v7] End-to-end RBAC & channel test suite
│   ├── test_products.py          # Schema & service mock tests
│   ├── test_routes.py            # Route controller integration tests
│   └── per_api_test.py           # Per-API route test suite
├── pytest.ini                    # Pytest configuration & warnings filters
└── run.py                        # Unified CLI runner (--env dev|prod)
```

---

## Quickstart Commands

### 1. Run Verification Test Suite
```powershell
pytest tests/test_hexagonal_architecture.py -s -v --env-file dev
```

### 2. Run Local Development Server
```powershell
python run.py --env dev
```
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`
- Alternative ReDoc: `http://127.0.0.1:8000/redoc`

### 3. Hot-Swappable Toy Authentication Tokens
- **Business Operator**: `Authorization: Bearer token-business-49`
- **Administrator**: `Authorization: Bearer token-admin-01`
