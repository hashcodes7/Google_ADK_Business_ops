# Business Operations Dashboard & Google ADK Backend (v2)

A production-ready enterprise backend architecture combining **FastAPI**, **Google Agent Development Kit (ADK)** with Gemini 2.5 Flash, and a dedicated **HTTPX Integration Layer** for upstream e-commerce services.

---

## What's New in v2: Integration Layer Architecture

In **v2**, the backend introduces a decoupled external service integration layer (`app/integrations/`):
- **Centralized HTTP Client (`EcommerceClient`)**: Consolidates upstream calls using `httpx` with managed timeouts and connection lifecycle.
- **Robust Exception Translation**: Automatically maps upstream HTTP status codes (e.g. 404, 5xx) and connection timeouts into domain exceptions (`ResourceNotFoundException`, `ExternalAPIException`).
- **Safe URI Encoding**: Sanitizes dynamic path segments (such as product categories) with `urllib.parse.quote`.
- **Dependency Cleanliness**: Cleaned redundant dependency listings in `requirements.txt`.

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
│   ├── integrations/             # [v2] External service integration layer
│   │   └── ecommerce_client.py   # HTTPX e-commerce API client & error handler
│   └── main.py                   # FastAPI factory & lifespan setup
├── agenticss/
│   └── agent.py                  # Google ADK Agent definition & tool functions
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
├── PROJECT_DOCUMENTATION.md      # Full architecture and API reference (this file)
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Production and runtime dependencies
└── run.py                        # Multi-environment CLI server runner
```

---

## Steps to Run

### 1. Environment Setup

Create and activate a Python virtual environment:

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create your local `.env.dev` file from the provided template:

```bash
cp environments/.env.example environments/.env.dev
```

Ensure the following variables are set in `environments/.env.dev`:

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

Start the FastAPI application via `run.py`:

```bash
# Development mode (with live reload enabled and environments/.env.dev loaded)
python run.py --env dev

# Production mode (reload disabled and environments/.env.prod loaded)
python run.py --env prod
```

- API Base URL: `http://localhost:8000`
- Swagger UI / OpenAPI Specs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

---

## Detailed File, Class, and Method Reference

### 1. External Integration Layer: `app/integrations/ecommerce_client.py` *(New in v2)*

Provides client abstraction over upstream e-commerce REST endpoints using `httpx`.

- **Classes:**
  - `EcommerceClient`:
    - `__init__(self)`: Reads `settings.ECOMMERCE_API_URL`, strips trailing slashes, and initializes the default request timeout to `10.0` seconds.
    - `_request(self, method: str, endpoint: str, **kwargs)`: Private core helper method.
      - Creates a scoped `httpx.Client(timeout=self.timeout)` session.
      - Dispatches HTTP requests with the given method and endpoint.
      - Handles `httpx.HTTPStatusError`:
        - Logs error with HTTP status code and endpoint.
        - Raises `ResourceNotFoundException` on `404`.
        - Raises `ExternalAPIException` on other 4xx/5xx responses.
      - Handles `httpx.RequestError`:
        - Logs network connection errors.
        - Raises `ExternalAPIException("Unable to connect to e-commerce backend.")`.
      - Returns parsed JSON response dictionary or list.
    - `get_all_products(self)`: Calls `GET /products` to retrieve the entire catalog.
    - `get_product(self, product_id: int)`: Calls `GET /products/{product_id}` to retrieve a single product by ID.
    - `get_products_by_category(self, category: str)`: Sanitizes the category string via `urllib.parse.quote(category, safe="")` and calls `GET /products/category/{category}`.
    - `create_product(self, product_data: dict)`: Calls `POST /products` passing `json=product_data` to register a new item.
    - `get_all_carts(self)`: Calls `GET /carts` to retrieve customer carts.
- **Exported Singletons:**
  - `ecommerce_client`: Pre-instantiated singleton instance of `EcommerceClient` ready for dependency injection or route handlers.

---

### 2. Application Entrypoint & Server: `run.py`

Handles command-line environment switching and boots the Uvicorn ASGI server.

- **Variables & Workflow:**
  - `parser`: `argparse.ArgumentParser` instance accepting `--env` (`dev` or `prod`, defaults to `dev`).
  - `load_dotenv(f"environments/.env.{args.env}", override=True)`: Dynamically loads the corresponding environment variables before the FastAPI application tree is initialized.
  - `uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=args.env == "dev")`: Starts the ASGI server with hot-reload enabled strictly in dev mode.

---

### 3. FastAPI Factory & Lifespan: `app/main.py`

Configures the FastAPI application instance, lifespan hooks, and global exception handlers.

- **Functions & Lifespans:**
  - `lifespan(app: FastAPI)`: Asynchronous context manager handling application startup and shutdown lifecycle events with logging.
  - `application_exception_handler(request: Request, exc: ApplicationException) -> JSONResponse`: Global exception interceptor catching any `ApplicationException` subclass and returning a uniform `{ "success": False, "error": exc.message }` JSON response with the corresponding HTTP status code.
  - `root() -> dict`: GET `/` route verifying system health and reporting application metadata.

---

### 4. Application Settings: `app/core/config.py`

Type-safe settings management using Pydantic Settings.

- **Classes:**
  - `Settings(BaseSettings)`:
    - *Fields:*
      - `APP_NAME: str`: Application display name (default: `"Business Operations Dashboard"`).
      - `APP_VERSION: str`: Application version (default: `"1.0.0"`).
      - `DEBUG: bool`: Debug toggle (default: `False`).
      - `API_V1_PREFIX: str`: Prefix for API v1 routes (default: `"/api/v1"`).
      - `ECOMMERCE_API_URL: str`: Base URL for upstream e-commerce service.
      - `GOOGLE_API_KEY: str`: Google Gemini API key.
      - `GOOGLE_GENAI_USE_VERTEXAI: bool`: Toggle Vertex AI mode.
      - `LOG_LEVEL: str`: Log level threshold (default: `"INFO"`).
    - `model_config`: `SettingsConfigDict` configured with `case_sensitive=True` and `extra="ignore"`.
- **Functions:**
  - `get_settings() -> Settings`: LRU-cached singleton provider returning the active configuration.

---

### 5. Custom Exceptions: `app/core/exceptions.py`

Standard domain exception hierarchy.

- **Classes & Constructors:**
  - `ApplicationException(Exception)`:
    - `__init__(self, message: str, status_code: int = 500)`: Root domain exception defining message and HTTP status code.
  - `ExternalAPIException(ApplicationException)`:
    - `__init__(self, message: str)`: Assigned HTTP status 502 (Bad Gateway) for external backend issues.
  - `ResourceNotFoundException(ApplicationException)`:
    - `__init__(self, message: str)`: Assigned HTTP status 404 (Not Found) for missing resources.
  - `ValidationException(ApplicationException)`:
    - `__init__(self, message: str)`: Assigned HTTP status 400 (Bad Request) for invalid payloads.

---

### 6. Centralized Logging: `app/core/logging.py`

Unified logging format across components.

- **Functions:**
  - `setup_logging(level: str = "INFO") -> None`:
    - Configures `logging.basicConfig` with format `%(asctime)s | %(levelname)s | %(name)s | %(message)s`, streaming to `sys.stdout` with `force=True`.

---

### 7. API Routing: `app/api/router.py`

FastAPI route organization.

- **Objects & Endpoints:**
  - `api_router`: `APIRouter` instance managing version 1 routes.
  - `health_check() -> dict`: GET `/health` route returning service status.

---

### 8. Google ADK Agent: `agenticss/agent.py`

Autonomous agent integration using Google ADK and Gemini.

- **Functions & Tools:**
  - `get_all_products() -> dict`: Catalog retrieval tool.
  - `get_product(product_id: int) -> dict`: Specific product retrieval tool.
  - `get_products_by_category(category: str) -> dict`: Categorized retrieval tool.
  - `create_product(title: str, price: float, description: str, category: str, image: str = "") -> dict`: Catalog creation tool.
  - `get_all_carts() -> dict`: Shopping cart inspection tool.
- **Agents:**
  - `root_agent`: `Agent` instance configured with name `"ecommerce_agent"`, model `"gemini-2.5-flash"`, instructions, and registered toolset.

---

### 9. Diagnostics & Testing: `tests/agent/`

- **`tests/agent/api_key_test.py`**: Verifies direct connectivity and API key validity against Google's `gemini-2.5-flash:generateContent` endpoint.
- **`tests/agent/model_list.py`**: Verifies API credentials by querying Google AI Studio's `v1beta/models` catalog.

---

## Security & Git Hygiene

- **Zero Secret Commits**: Real environment secrets (`environments/.env.dev`, `environments/.env.prod`) are permanently blocked by `.gitignore`.
- **Database & State Protection**: SQLite files (`*.db`, `*.sqlite`, `*.sqlite3`) and ADK session cache (`.adk/`) are ignored.
- **Clean Templates**: Only template configuration (`environments/.env.example`) with empty dummy values is tracked.
