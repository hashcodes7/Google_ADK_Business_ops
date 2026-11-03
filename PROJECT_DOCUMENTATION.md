# Business Operations Dashboard & Google ADK Backend

A robust backend architecture integrating FastAPI with Google Agent Development Kit (ADK) and Gemini 2.5 Flash for enterprise business and e-commerce operations.

---

## Architecture Overview

```
Business_ops_GoogleADK/
├── app/                      # Main FastAPI application package
│   ├── api/
│   │   └── router.py         # Versioned API routes registration
│   ├── core/
│   │   ├── config.py         # Environment-driven Pydantic settings
│   │   ├── exceptions.py     # Custom application exception hierarchy
│   │   └── logging.py        # Centralized logging configuration
│   └── main.py               # FastAPI factory & lifespan setup
├── agenticss/
│   └── agent.py              # Google ADK Agent definition & tool functions
├── environments/
│   ├── .env.example          # Environment template (safe for git)
│   ├── .env.dev              # Development environment variables (git-ignored)
│   └── .env.prod             # Production environment variables (git-ignored)
├── tests/
│   ├── agent/
│   │   ├── api_key_test.py   # Direct Gemini API connectivity test
│   │   └── model_list.py     # Gemini model catalog inspection test
│   ├── test_health.py        # Health endpoint tests
│   └── test_products.py      # Product endpoint tests
├── .gitignore                # Git ignore configuration
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Production and runtime dependencies
└── run.py                    # Multi-environment CLI server runner
```

---

## Steps to Run

### 1. Environment Setup

Create and activate a virtual environment:

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create your local `.env.dev` from the template:

```bash
cp environments/.env.example environments/.env.dev
```

Populate the required configuration in `environments/.env.dev`:

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

Start the FastAPI application with `run.py`:

```bash
# Development mode (with hot-reload and environments/.env.dev)
python run.py --env dev

# Production mode (without reload and environments/.env.prod)
python run.py --env prod
```

- API Base URL: `http://localhost:8000`
- Swagger UI Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/v1/health`

---

## Detailed File, Class, and Method Reference

### 1. Application Entrypoint & Server: `run.py`

Handles command-line environment switching and launches the Uvicorn ASGI server.

- **Variables & Flow:**
  - `parser`: `argparse.ArgumentParser` configured to accept `--env` (`dev` or `prod`, default: `dev`).
  - `load_dotenv(f"environments/.env.{args.env}", override=True)`: Dynamically loads the corresponding environment variables before FastAPI initializes.
  - `uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=args.env == "dev")`: Starts the server with live reload enabled strictly for dev mode.

---

### 2. FastAPI Factory & Lifespan: `app/main.py`

Defines the FastAPI application lifecycle, global exception handling, and root endpoints.

- **Functions & Lifespans:**
  - `lifespan(app: FastAPI)`: Asynchronous context manager managing application startup and shutdown events, logging application startup state.
  - `application_exception_handler(request: Request, exc: ApplicationException) -> JSONResponse`: Global exception handler that catches any custom `ApplicationException` and formats it into a uniform `{ "success": False, "error": exc.message }` JSON response with matching HTTP status codes.
  - `root() -> dict`: Root GET (`/`) endpoint verifying service availability and returning application name, version, and running state.

---

### 3. Application Settings: `app/core/config.py`

Type-safe application configuration powered by Pydantic Settings.

- **Classes:**
  - `Settings(BaseSettings)`:
    - *Fields:*
      - `APP_NAME: str`: Display name of the backend service.
      - `APP_VERSION: str`: Application semantic version.
      - `DEBUG: bool`: Debug mode flag.
      - `API_V1_PREFIX: str`: Base prefix for version 1 API routes (default: `/api/v1`).
      - `ECOMMERCE_API_URL: str`: Target URL for the e-commerce upstream backend.
      - `GOOGLE_API_KEY: str`: Gemini / Google ADK API key.
      - `GOOGLE_GENAI_USE_VERTEXAI: bool`: Toggle between Google AI Studio and Vertex AI.
      - `LOG_LEVEL: str`: Logging severity threshold (`DEBUG`, `INFO`, etc.).
    - `model_config`: `SettingsConfigDict` configured with `case_sensitive=True` and `extra="ignore"`.
- **Functions:**
  - `get_settings() -> Settings`: LRU-cached singleton provider returning the cached `Settings` instance.

---

### 4. Custom Exceptions: `app/core/exceptions.py`

Standardized exception hierarchy for application errors.

- **Classes & Constructors:**
  - `ApplicationException(Exception)`:
    - `__init__(self, message: str, status_code: int = 500)`: Base exception defining error message and default HTTP status code 500.
  - `ExternalAPIException(ApplicationException)`:
    - `__init__(self, message: str)`: Raised when upstream external API calls fail; assigns HTTP status 502 (Bad Gateway).
  - `ResourceNotFoundException(ApplicationException)`:
    - `__init__(self, message: str)`: Raised when requested resources are missing; assigns HTTP status 404 (Not Found).
  - `ValidationException(ApplicationException)`:
    - `__init__(self, message: str)`: Raised on bad request or schema validation errors; assigns HTTP status 400 (Bad Request).

---

### 5. Centralized Logging: `app/core/logging.py`

Configures structured console logging across the application.

- **Functions:**
  - `setup_logging(level: str = "INFO") -> None`:
    - Configures `logging.basicConfig` with format `%(asctime)s | %(levelname)s | %(name)s | %(message)s`, streaming to `sys.stdout` with `force=True`.

---

### 6. API Routing: `app/api/router.py`

Defines versioned endpoint routing.

- **Objects & Endpoints:**
  - `api_router`: `APIRouter` instance mounting versioned endpoints.
  - `health_check() -> dict`: GET `/health` endpoint returning health status and service identifier.

---

### 7. Google ADK Agent: `agenticss/agent.py`

Defines the e-commerce operations agent and tool functions using the Google Agent Development Kit (ADK).

- **Tool Functions:**
  - `get_all_products() -> dict`: Fetches the entire product catalog from the e-commerce backend (`GET /products`).
  - `get_product(product_id: int) -> dict`: Fetches a single product by its unique integer identifier (`GET /products/{product_id}`).
  - `get_products_by_category(category: str) -> dict`: Queries products filtered by a category name (`GET /products/category/{category}`).
  - `create_product(title: str, price: float, description: str, category: str, image: str = "") -> dict`: Posts a new product payload to the catalog (`POST /products`).
  - `get_all_carts() -> dict`: Retrieves customer shopping cart data (`GET /carts`).
- **Agents:**
  - `root_agent`: `Agent` instance configured with name `"ecommerce_agent"`, model `"gemini-2.5-flash"`, operational instructions, and tool bindings.

---

### 8. Diagnostic Tests: `tests/agent/`

Verification scripts for testing Google AI connectivity and credentials without starting the full web server.

- **`tests/agent/api_key_test.py`**:
  - Loads environment settings and tests direct `generateContent` requests against `gemini-2.5-flash` using `x-goog-api-key`.
- **`tests/agent/model_list.py`**:
  - Tests connectivity by querying the `v1beta/models` endpoint for available Gemini models.

---

## Security & Git Hygiene

- **Real secrets** (`.env.dev`, `.env.prod`) are strictly ignored via `.gitignore` and never committed.
- **SQLite / ADK session databases** (`*.db`, `.adk/`) are ignored to prevent leaking runtime conversation states.
- **Templates** (`environments/.env.example`) contain empty placeholder values for safe version control.
