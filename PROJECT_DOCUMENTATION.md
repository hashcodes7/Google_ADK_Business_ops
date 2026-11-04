# Business Operations Dashboard & Google ADK Backend (v8)

A production-ready enterprise backend architecture combining **Hexagonal Architecture (Ports & Adapters)**, **Hot-Swappable Bearer Authentication**, **Password Gate (`123456`)**, **Role-Based Access Control (RBAC)**, an isolated **Handcrafted Utilitarian Frontend**, **FastAPI Modular Route Controllers**, **Pydantic Schemas**, a dedicated **Service Layer**, **Google Agent Development Kit (ADK)** with Gemini (`gemini-flash-lite-latest`), an **HTTPX Integration Layer**, and a **Dynamic Environment-Injected Test Suite**.

---

## What's New in v8: Handcrafted Frontend, Password Gate & Offline Fallback

In **v8**, the user interface was decoupled into an isolated folder and redesigned with a tactile, human-crafted utilitarian aesthetic:
- **Handcrafted, Utilitarian Frontend (`frontend/`)**:
  - Replaced hyper-polished AI gradients with a workshop/drafting aesthetic using mechanical typography (**Courier Prime** and **IBM Plex Sans**), warm paper backgrounds (`#F7F5F0`), ink drafting borders, and offset tactile drop shadows (`2px 2px 0px #1C1917`).
  - Isolated architecture: Contains `index.html`, `css/style.css`, and modular vanilla JS controllers (`api.js`, `dashboard.js`, `products.js`, `carts.js`, `assistant.js`).
- **Offline Fallback Screen**:
  - If the FastAPI backend is offline, the UI displays a clean fallback card informing the user and providing the `python run.py --env dev` command with manual retry.
- **Universal Password Gate (`123456`)**:
  - Direct operator login (`POST /api/v1/auth/login`) with accounts `user49` (Business) and `admin` (Admin) authenticated with password `123456`.
- **CORS Support**: `CORSMiddleware` configured to allow seamless access from local file systems and frontends.
- **Bootstrap URL Print**: Displays `backend URL is : http://127.0.0.1:8000` on server startup.
- **Milestone 8 Documentation**:
  - `adk_ops_docs/v8_frontend_and_auth_gate.md`

---

## Architecture Overview

```
Business_ops_GoogleADK/
├── app/                          # Main FastAPI application package
│   ├── api/
│   │   ├── routes/               # Modular API route controllers
│   │   │   ├── auth.py           # [v8] Login (POST /auth/login) & Me endpoints
│   │   │   ├── carts.py          # GET /api/v1/carts/
│   │   │   ├── products.py       # GET, POST /api/v1/products/
│   │   │   └── users.py          # [User-Only] POST /api/v1/users/ (Admin)
│   │   └── router.py             # Route aggregator
│   ├── core/
│   │   ├── auth.py               # [v7/v8] Hot-swappable Auth Adapter & Password check
│   │   ├── security.py           # SecurityContext, Roles & require_permission
│   │   ├── config.py             # Environment settings (Gemini, FakeStore)
│   │   ├── exceptions.py         # Custom application exceptions (401, 403, 404, 502)
│   │   └── logging.py            # Centralized logging configuration
│   ├── ports/                    # Hexagonal Outbound Ports
│   │   └── ecommerce_port.py     # Protocol for downstream commerce integrations
│   ├── integrations/             # Outbound Driven Adapters
│   │   └── ecommerce_client.py   # HTTPX client implementing ecommerce_port
│   ├── schemas/                  # Request & Response Pydantic models
│   │   ├── product.py            # ProductCreate, ProductResponse schemas
│   │   └── user.py               # UserCreate, UserResponse schemas
│   ├── services/                 # Shared domain business services
│   │   ├── cart_service.py       # Shopping cart service (RBAC checked)
│   │   ├── product_service.py    # Product operations service (RBAC checked)
│   │   └── user_service.py       # User provisioning service (RBAC checked)
│   └── main.py                   # FastAPI app factory, CORS & lifespan setup
├── agents/                       # Google ADK Inbound Adapter
│   ├── agent.py                  # Agent orchestrator (gemini-flash-lite-latest)
│   └── tools/
│       ├── cart_tools.py         # Carts tools + [Agent-Only] inspect_cart_by_id
│       └── product_tools.py      # Product catalog tools
├── frontend/                     # [v8] Decoupled Handcrafted Frontend
│   ├── index.html                # 4-zone single-page app
│   ├── css/style.css             # Workshop/drafting design system
│   ├── js/                       # Inbound client controllers
│   └── assets/                   # Static media
├── adk_ops_docs/                 # Versioned Milestone Guides
│   ├── v1_run_steps.md
│   ├── v2_calling_an_api.md
│   ├── v3_architecture_and_services.md
│   ├── v4_architecture_and_testing.md
│   ├── v5_architecture_and_routing.md
│   ├── v6_hexagonal_architecture.md
│   ├── v7_hexagonal_auth_and_channels.md
│   ├── v7_tools_and_api_guide.md
│   └── v8_frontend_and_auth_gate.md # [v8] Frontend, auth gate & offline docs
├── environments/
│   ├── .env.example
│   ├── .env.dev
│   └── .env.prod
├── tests/
│   ├── test_hexagonal_architecture.py
│   ├── test_products.py
│   ├── test_routes.py
│   └── per_api_test.py
├── pytest.ini
└── run.py                        # Unified CLI runner (--env dev|prod)
```

---

## Quickstart Commands

### 1. Run Local Backend Server
```powershell
python run.py --env dev
```
Terminal will output:
```text
⚡ Starting Business Operations Backend (dev)
backend URL is : http://127.0.0.1:8000
```

### 2. Open Handcrafted Frontend
Open `frontend/index.html` in your browser.
- **Login Password**: `123456`
- **User Accounts**: `user49` (Business) or `admin` (Admin).

### 3. Run Backend Verification Tests
```powershell
pytest tests/test_hexagonal_architecture.py -s -v --env-file dev
```
