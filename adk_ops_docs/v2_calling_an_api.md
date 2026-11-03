# Milestone 2: How We Call an External API (`v2_calling_an_api.md`)

> ### ⚡ Primary Command
> ```powershell
> python -c "from dotenv import load_dotenv; load_dotenv('environments/.env.dev'); from app.integrations.ecommerce_client import ecommerce_client; print(ecommerce_client.get_product(1))"
> ```
> *(Or launch server: `python run.py --env dev`)*

This guide explains the foundational pattern for calling an external API in Python within this project. It documents the core architecture, configuration flow, execution mechanics, and error-handling principles implemented in **v2**.

---

## 1. The Core Pattern

In this project, external API calls are centralized inside a dedicated integration layer:
[`app/integrations/ecommerce_client.py`](file:///c:/Users/Harsh/HiHarsh/Coding/Python/Business_ops_GoogleADK/app/integrations/ecommerce_client.py).

Instead of making ad-hoc `requests` or `httpx` calls scattered across routers, controllers, or agent tools:
1. Environment variables define the remote base URL (`ECOMMERCE_API_URL`).
2. Pydantic validates and serves the setting via `app.core.config.settings`.
3. A client class (`EcommerceClient`) encapsulates HTTP transport, connection lifecycle, and timeout rules using `httpx`.
4. Domain exceptions translate raw HTTP status codes into standardized application responses.

---

## 2. Step-by-Step Code Walkthrough

Here is the complete, minimal pattern used in our codebase:

```python
import logging
from urllib.parse import quote
import httpx

from app.core.config import settings
from app.core.exceptions import (
    ExternalAPIException,
    ResourceNotFoundException,
)

logger = logging.getLogger(__name__)

class EcommerceClient:
    def __init__(self):
        # 1. Base URL loaded from environment settings
        self.base_url = settings.ECOMMERCE_API_URL.rstrip("/")
        # 2. Strict timeout prevents hanging requests
        self.timeout = 10.0

    def _request(self, method: str, endpoint: str, **kwargs):
        """Centralized dispatcher for all HTTP calls."""
        url = f"{self.base_url}{endpoint}"

        try:
            # 3. Context-managed HTTP client for clean socket closing
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)

            # 4. Raises HTTPStatusError if status is 4xx or 5xx
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            logger.error(
                "E-commerce API returned HTTP %s for %s",
                exc.response.status_code,
                endpoint,
            )
            # 5. Translate upstream 404 into domain ResourceNotFoundException
            if exc.response.status_code == 404:
                raise ResourceNotFoundException(
                    "Requested e-commerce resource was not found."
                ) from exc

            # 6. Translate any other upstream error into ExternalAPIException (502)
            raise ExternalAPIException(
                "E-commerce backend returned an error."
            ) from exc

        except httpx.RequestError as exc:
            # 7. Handles DNS failures, network connection drops, timeouts
            logger.exception("E-commerce backend connection failed")
            raise ExternalAPIException(
                "Unable to connect to e-commerce backend."
            ) from exc

    # Example API Method: Simple GET call
    def get_product(self, product_id: int):
        return self._request("GET", f"/products/{product_id}")

    # Example API Method: Parameterized GET with URL escaping
    def get_products_by_category(self, category: str):
        safe_category = quote(category, safe="")
        return self._request("GET", f"/products/category/{safe_category}")

    # Example API Method: POST call with JSON payload
    def create_product(self, product_data: dict):
        return self._request("POST", "/products", json=product_data)


# Export a ready-to-use singleton
ecommerce_client = EcommerceClient()
```

---

## 3. How to Call It in Practice

Whenever any part of the project (such as a FastAPI route or an ADK agent tool) needs e-commerce data, it simply imports the client and calls the method directly:

### Example: Calling from Python Shell / Script

```python
from dotenv import load_dotenv

# Step A: Load the environment configuration
load_dotenv("environments/.env.dev")

# Step B: Import the client
from app.integrations.ecommerce_client import ecommerce_client

# Step C: Call the API
product = ecommerce_client.get_product(product_id=1)
print("Product title:", product["title"])
print("Product price:", product["price"])
```

### Example: Calling inside a FastAPI Route

```python
from fastapi import APIRouter
from app.integrations.ecommerce_client import ecommerce_client

router = APIRouter()

@router.get("/products/{product_id}")
def fetch_product(product_id: int):
    # One line call - exceptions (404, 502) are automatically caught 
    # and returned as uniform JSON responses by app/main.py
    return ecommerce_client.get_product(product_id)
```

---

## 4. Key Rules We Follow

1. **Never Hardcode URLs or Keys**: All endpoints originate from `settings.ECOMMERCE_API_URL` configured in `environments/.env.*`.
2. **Always Use Timeouts**: `timeout=10.0` ensures network congestion upstream never locks the server workers indefinitely.
3. **Always Sanitize User URL Parameters**: Any dynamic path parameter (like category names or search slugs) passes through `urllib.parse.quote` to protect against path traversal or bad URL encoding.
4. **Context Manager Lifetime**: `with httpx.Client(...) as client:` guarantees TCP connection sockets are cleanly released after execution.
5. **Exception Translation**: Upstream HTTP errors are never leaked raw; they are caught and mapped into our custom `ApplicationException` hierarchy, maintaining a consistent API contract.
