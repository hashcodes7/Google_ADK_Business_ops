# Milestone 6: Hexagonal Architecture with Shared Application Operations (`v6_hexagonal_architecture.md`)

> ### ⚡ Primary Command
> ```powershell
> pytest tests/test_hexagonal_architecture.py -s -q --env-file dev
> ```
> *(Or launch server: `python run.py --env dev`)*

This document details **Milestone 6 (v6)**: Refactoring the backend into **Hexagonal Architecture (Ports and Adapters)** with a centralized **Shared Application Layer**, trusted **SecurityContext**, and decoupled inbound adapters (FastAPI & Google ADK).

---

## 1. Architectural Model

```
       INBOUND ADAPTER 1                          INBOUND ADAPTER 2
      FastAPI Controllers                        Google ADK Agent Tools
   (app/api/routes/*.py)                          (agents/tools/*.py)
             │                                             │
      Actor: "human"                                 Actor: "agent"
             │                                             │
             └──────────────────────┬──────────────────────┘
                                    │ Trusted SecurityContext
                                    │ (user_id="User_49", role="Business")
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │               SHARED APPLICATION LAYER                 │
       │    app/application/product_ops.py & cart_ops.py        │
       │                                                        │
       │  - Centralized Authorization (require_permission)      │
       │  - Business Rules & Workflow Orchestration             │
       │  - Shared Input Validation (Pydantic Schemas)          │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼ Outbound Port Protocol
       ┌────────────────────────────────────────────────────────┐
       │               OUTBOUND DRIVEN ADAPTER                  │
       │    app/integrations/ecommerce_client.py                │
       │    (Implements app/ports/ecommerce_port.py)            │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       Upstream Backend Services (FakeStore API / External Database)
```

---

## 2. Key Hexagonal Components

### A. Trusted Security Context (`app/core/security.py`)
- Injected into operations via `SecurityContext(user_id=..., role=..., actor=...)`.
- Defaults to environment settings (`AUTH_USER_ID="User_49"`, `AUTH_ROLE="Business"`).
- Distinguishes traffic source:
  - Web REST calls $\rightarrow$ `actor="human"`
  - Google ADK agent tool invocations $\rightarrow$ `actor="agent"`
- `require_permission(context, allowed_actors=..., required_role=...)`: Centralized authorization guard.

### B. Shared Application Operations (`app/application/`)
- **`ProductOperations` (`app/application/product_ops.py`)**:
  - Handles `get_all_products`, `get_product`, `get_products_by_category`, and `create_product`.
  - Validates request payloads with `ProductCreate`.
  - Enforces RBAC permissions before calling outbound ports.
- **`CartOperations` (`app/application/cart_ops.py`)**:
  - Centralizes cart queries and access checks.

### C. Outbound Port (`app/ports/ecommerce_port.py`)
- Python `Protocol` defining abstract dependencies required by the application layer.
- `app/integrations/ecommerce_client.py` satisfies this protocol without coupling to business logic.

### D. Inbound Adapters
1. **FastAPI Web Adapter (`app/api/routes/`)**:
   - Routes inject `create_security_context(actor="human")` and delegate to shared application operations.
2. **Google ADK Agent Adapter (`agents/`)**:
   - `agents/tools/product_tools.py` & `agents/tools/cart_tools.py` inject `create_security_context(actor="agent")` and call shared operations directly.
   - LLM reasoning and prompt orchestration live strictly in `agents/agent.py`.
