# Milestone 7: Hexagonal Architecture, Hot-Swappable Bearer Authentication & User vs Agent Channels (`v7_hexagonal_auth_and_channels.md`)

> ### ⚡ Primary Command
> ```powershell
> pytest tests/test_hexagonal_architecture.py -s -v --env-file dev
> ```
> *(Or run the application server: `python run.py --env dev`)*

This document details **Milestone 7 (v7)**: Consolidating **Hexagonal Architecture (Ports & Adapters)** with a **Hot-Swappable Authentication Adapter** (`app/core/auth.py`), strict Role-Based Access Control (`app/core/security.py`), and explicit **Channel Isolation** between Human Users (REST API) and AI Agents (Google ADK Tools).

---

## 1. Architectural Architecture Diagram

```
       INBOUND ADAPTER 1 (REST / User)            INBOUND ADAPTER 2 (ADK / Agent)
       FastAPI Route Controllers                  Google ADK Agent Tools
       (app/api/routes/*.py)                      (agents/tools/*.py)
       - Header: Authorization: Bearer <token>    - Embedded Context Generator
                 │                                          │
                 ▼                                          │
       ┌────────────────────────┐                           │
       │   HOT-SWAPPABLE AUTH   │                           │
       │   (app/core/auth.py)   │                           │
       └─────────┬──────────────┘                           │
                 │                                          │
                 │ SecurityContext                          │ SecurityContext
                 │ (user_id, role, actor="human")           │ (user_id="adk_agent", role, actor="agent")
                 └────────────────────┬─────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────────┐
       │                   SHARED APPLICATION SERVICES                   │
       │         (app/services/product_service, cart_service,            │
       │                     user_service)                               │
       │                                                                 │
       │  - Centralized Security Guard: require_permission(context, ...) │
       │  - Zero Direct DB / HTTP Calls (Outbound Port Invocation)       │
       │  - Schema & Payload Sanitization (Pydantic)                     │
       └──────────────────────────────┬──────────────────────────────────┘
                                      │
                                      ▼ Outbound Port Interface
       ┌─────────────────────────────────────────────────────────────────┐
       │                   OUTBOUND PORT DEFINITION                      │
       │                  (app/ports/ecommerce_port.py)                  │
       └──────────────────────────────┬──────────────────────────────────┘
                                      │
                                      ▼ Implemented by
       ┌─────────────────────────────────────────────────────────────────┐
       │                   OUTBOUND DRIVEN ADAPTER                       │
       │             (app/integrations/ecommerce_client.py)              │
       │  - HTTPX Network Protocol to Upstream FakeStore API             │
       │  - Status Error Translation to Domain Application Exceptions    │
       └─────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Pillars

### A. Hot-Swappable Authentication Adapter (`app/core/auth.py`)
All token parsing, user resolution, and HTTP Header extraction are encapsulated in a single file: `app/core/auth.py`. 
- **Modular Isolation**: No business logic or service file knows *how* tokens are decoded or verified.
- **Toy Implementation**: Maps Static Bearer tokens to domain users:
  - `Bearer token-business-49` ➔ `user_id="User_49"`, `role=Role.BUSINESS`, `actor="human"`
  - `Bearer token-admin-01` ➔ `user_id="Admin_01"`, `role=Role.ADMIN`, `actor="human"`
- **Production Ready Swap**: To replace with JWT, OAuth2, or Auth0, only `app/core/auth.py` needs to be edited. The services and routes remain untouched.

### B. Security Context & Role-Based Permissions (`app/core/security.py`)
```python
class Role(str, Enum):
    BUSINESS = "Business"
    ADMIN = "Admin"

@dataclass(frozen=True)
class SecurityContext:
    user_id: str
    role: Role
    actor: ActorType = "human"  # "human" or "agent"
```
The central permission engine uses `require_permission(context: SecurityContext, permission: Permission)`:
- `Role.BUSINESS`: `PRODUCTS_READ`, `CARTS_READ`
- `Role.ADMIN`: `PRODUCTS_READ`, `CARTS_READ`, `PRODUCTS_WRITE`, `USERS_WRITE`
- Missing context raises `AuthenticationException` (HTTP 401).
- Insufficient role raises `UnauthorizedException` (HTTP 403).

### C. Channel Isolation: User vs Agent vs Shared
The system establishes three distinct functional channels across the application:

| Channel Type | Endpoint / Function | Access Inbound Adapter | Allowed Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| **User-Only** | `POST /api/v1/users/` | REST API (`app/api/routes/users.py`) | `Role.ADMIN` | User account creation. Explicitly omitted from Google ADK agent tools to prevent accidental LLM account generation. |
| **Agent-Only** | `inspect_cart_by_id(cart_id)` | Google ADK (`agents/tools/cart_tools.py`) | `Role.BUSINESS` / `ADMIN` | Cart inspection tool exposed directly to Gemini LLM for operational audit. Not mounted on FastAPI REST routes. |
| **Shared** | `GET /api/v1/products/`<br>`GET /api/v1/carts/` | REST API + Google ADK (`agents/tools/`) | `Role.BUSINESS` / `ADMIN` | Catalog browsing and shopping cart retrieval accessible by both human operators and autonomous agents. |

---

## 3. Directory Layout

```
Business_ops_GoogleADK/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── carts.py          # GET /api/v1/carts/
│   │   │   ├── products.py       # GET, POST /api/v1/products/
│   │   │   └── users.py          # [User-Only] POST /api/v1/users/
│   │   └── router.py             # Route aggregator
│   ├── core/
│   │   ├── auth.py               # [Milestone 7] Hot-swappable Auth Adapter
│   │   ├── security.py           # SecurityContext, Roles, require_permission
│   │   ├── exceptions.py         # AuthenticationException, UnauthorizedException
│   │   └── config.py             # Settings (gemini-flash-lite-latest, ECOMMERCE_API_URL)
│   ├── ports/
│   │   └── ecommerce_port.py     # Hexagonal Outbound Protocol
│   ├── integrations/
│   │   └── ecommerce_client.py   # Driven HTTPX Adapter implementing port
│   ├── schemas/
│   │   ├── product.py            # ProductCreate, ProductResponse
│   │   └── user.py               # UserCreate, UserResponse
│   └── services/
│       ├── product_service.py    # Shared Product Service
│       ├── cart_service.py       # Shared Cart Service
│       └── user_service.py       # Shared User Service
├── agents/
│   ├── agent.py                  # Google ADK Agent orchestrator
│   └── tools/
│       ├── cart_tools.py         # Shared & Agent-only tools (inspect_cart_by_id)
│       └── product_tools.py      # Shared product tools
└── tests/
    └── test_hexagonal_architecture.py # v7 Verification Suite
```

---

## 4. Verification

Execute the test suite to verify all auth guards, role boundaries, and channel constraints:
```powershell
pytest tests/test_hexagonal_architecture.py -s -v --env-file dev
```

Expected output:
- `💚 [Result] Auth Guard -> test_hexagonal_architecture.py -> None context rejected with AuthenticationException`
- `💚 [Result] RBAC Read -> test_hexagonal_architecture.py -> Role.BUSINESS permitted for PRODUCTS_READ`
- `💚 [Result] RBAC Selective Guard -> test_hexagonal_architecture.py -> Role.BUSINESS denied PRODUCTS_WRITE`
- `💚 [Result] User-Only API -> test_hexagonal_architecture.py -> POST /users restricted to Admin, denied to Business`
- `💚 [Result] Agent-Only API -> test_hexagonal_architecture.py -> inspect_cart_by_id executed successfully via shared service`
- `💚 [Result] Agent Inbound Adapter -> test_hexagonal_architecture.py -> ADK tools executed with agent context`
