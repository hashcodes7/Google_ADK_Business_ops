# Milestone 7: Tools and API Access Cookbook (`v7_tools_and_api_guide.md`)

> ### ⚡ Primary Command
> ```powershell
> python run.py --env dev
> ```
> *(Starts the FastAPI server on `http://127.0.0.1:8000` with Swagger UI at `http://127.0.0.1:8000/docs`)*

This guide provides a comprehensive catalog of all **REST API endpoints** and **Google ADK Agent tools** in Milestone 7, detailing authentication tokens, required roles, and sample request payloads.

---

## 1. Authentication Credentials (Toy Tokens)

Include the token in the `Authorization` HTTP header for REST API requests:
```http
Authorization: Bearer <TOKEN>
```

| Token | Identity | Role | Allowed Permissions |
| :--- | :--- | :--- | :--- |
| `token-business-49` | `User_49` | `Business` | `PRODUCTS_READ`, `CARTS_READ` |
| `token-admin-01` | `Admin_01` | `Admin` | `PRODUCTS_READ`, `CARTS_READ`, `PRODUCTS_WRITE`, `USERS_WRITE` |

---

## 2. API & Tool Catalog Matrix

| Operation | Channel | Path / Tool Name | Method | Minimum Role |
| :--- | :--- | :--- | :--- | :--- |
| **Get All Products** | **Shared** (REST + Agent) | `/api/v1/products/` \| `fetch_all_products()` | `GET` | `Business` |
| **Get Product by ID** | **Shared** (REST + Agent) | `/api/v1/products/{id}` \| `fetch_product_by_id(id)` | `GET` | `Business` |
| **Get Products by Category** | **REST** | `/api/v1/products/category/{cat}` | `GET` | `Business` |
| **Create Product** | **Shared** (REST + Agent) | `/api/v1/products/` \| `create_new_product(...)` | `POST` | `Admin` |
| **Get All Carts** | **Shared** (REST + Agent) | `/api/v1/carts/` \| `fetch_recent_carts()` | `GET` | `Business` |
| **Inspect Cart by ID** | **Agent-Only** | `inspect_cart_by_id(cart_id)` | Tool | `Business` |
| **Create User** | **User-Only** (REST) | `/api/v1/users/` | `POST` | `Admin` |

---

## 3. How to Access: REST API Endpoints

### A. [Shared] List All Products
- **URL**: `GET /api/v1/products/`
- **Headers**: `Authorization: Bearer token-business-49`
- **cURL**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/products/" \
       -H "Authorization: Bearer token-business-49"
  ```

### B. [Shared] Get Product by ID
- **URL**: `GET /api/v1/products/1`
- **Headers**: `Authorization: Bearer token-business-49`
- **cURL**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/products/1" \
       -H "Authorization: Bearer token-business-49"
  ```

### C. [Shared] Create a Product (Admin Only)
- **URL**: `POST /api/v1/products/`
- **Headers**: 
  - `Authorization: Bearer token-admin-01`
  - `Content-Type: application/json`
- **Payload**:
  ```json
  {
    "title": "Industrial Wireless Scanner",
    "price": 149.99,
    "description": "High durability laser scanner",
    "category": "electronics",
    "image": "https://fakestoreapi.com/img/scanner.jpg"
  }
  ```
- **cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/v1/products/" \
       -H "Authorization: Bearer token-admin-01" \
       -H "Content-Type: application/json" \
       -d "{\"title\": \"Industrial Wireless Scanner\", \"price\": 149.99, \"description\": \"High durability laser scanner\", \"category\": \"electronics\", \"image\": \"https://fakestoreapi.com/img/scanner.jpg\"}"
  ```

### D. [Shared] List Carts
- **URL**: `GET /api/v1/carts/`
- **Headers**: `Authorization: Bearer token-business-49`
- **cURL**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/carts/" \
       -H "Authorization: Bearer token-business-49"
  ```

### E. [User-Only] Create User Account (Admin Only)
*Notice: This endpoint is explicitly not exposed to AI Agent tools to enforce segregation of sensitive user provisioning.*
- **URL**: `POST /api/v1/users/`
- **Headers**: 
  - `Authorization: Bearer token-admin-01`
  - `Content-Type: application/json`
- **Payload**:
  ```json
  {
    "username": "sarah_ops",
    "email": "sarah@company.internal",
    "password": "SecurePassword123!"
  }
  ```
- **cURL**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
       -H "Authorization: Bearer token-admin-01" \
       -H "Content-Type: application/json" \
       -d "{\"username\": \"sarah_ops\", \"email\": \"sarah@company.internal\", \"password\": \"SecurePassword123!\"}"
  ```

---

## 4. How to Access: Google ADK Agent Tools

Agent tools execute via `agents/agent.py` and run against the shared service layer with an agent `SecurityContext`.

### A. Python Programmatic Invocation
```python
from agents.tools.cart_tools import inspect_cart_by_id, fetch_recent_carts
from agents.tools.product_tools import fetch_all_products, create_new_product

# 1. [Shared] Fetch product catalog
products = fetch_all_products()

# 2. [Shared] Fetch active carts
carts = fetch_recent_carts()

# 3. [Agent-Only] Inspect a specific cart for audit (not on REST routes)
cart_detail = inspect_cart_by_id(cart_id=1)

# 4. [Shared Admin] Create product via Agent tool
new_item = create_new_product(
    title="Agent Created Gadget",
    price=89.50,
    description="Tool-assisted generation",
    category="electronics",
    image="http://example.com/gadget.png"
)
```

### B. Natural Language via Gemini CLI / Runner
When interacting with the Google ADK Agent (`python -m agents.agent`):
- *"List the latest products in the catalog."* ➔ Triggers `fetch_all_products`
- *"Inspect shopping cart #2 and summarize items."* ➔ Triggers `inspect_cart_by_id`
- *"Add a new product titled 'Thermal Label Roll' priced at $12.50."* ➔ Triggers `create_new_product`
- *"Create a new user account."* ➔ The agent will reply that user management is not available as a tool and must be executed by an Admin via the REST API.
