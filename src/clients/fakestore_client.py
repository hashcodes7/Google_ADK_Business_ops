import logging
from typing import Any, List, Optional
import httpx
from src.schemas.product import Product

logger = logging.getLogger(__name__)


class FakeStoreError(Exception):
    """Base exception for FakeStoreAPI client operations."""
    pass


class FakeStoreItemNotFoundError(FakeStoreError):
    """Raised when a requested product or entity is not found upstream."""
    pass


class FakeStoreUpstreamError(FakeStoreError):
    """Raised when upstream service returns an unrecoverable HTTP status or network failure."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class FakeStoreClient:
    """
    Asynchronous client for interacting with the external FakeStoreAPI.
    
    Reuses an underlying httpx.AsyncClient session for connection pooling,
    keep-alive, and low-latency upstream request execution.
    """

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def get_products(
        self,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> List[Product]:
        """
        Fetch a list of products with optional limit and sort ordering.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        try:
            response = await self._client.get("/products", params=params)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.warning("Unexpected response format from FakeStore /products: %s", type(data))
                return []
            return [Product.model_validate(item) for item in data]
        except httpx.HTTPStatusError as exc:
            logger.error("FakeStore API HTTP error on /products: status=%d, detail=%s", exc.response.status_code, exc)
            raise FakeStoreUpstreamError(
                f"FakeStore API error: {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("FakeStore API connection failure on /products: %s", exc)
            raise FakeStoreUpstreamError("Failed to reach FakeStore API upstream service") from exc

    async def get_product(self, product_id: int) -> Product:
        """
        Fetch a single product by its unique integer identifier.
        Raises FakeStoreItemNotFoundError if the item is missing.
        """
        try:
            response = await self._client.get(f"/products/{product_id}")
            if response.status_code == 404:
                raise FakeStoreItemNotFoundError(f"Product with ID {product_id} not found.")

            response.raise_for_status()

            # FakeStoreAPI returns empty string or JSON null for non-existent IDs instead of 404
            text = response.text.strip()
            if not text or text == "null":
                raise FakeStoreItemNotFoundError(f"Product with ID {product_id} not found.")

            data = response.json()
            if not data:
                raise FakeStoreItemNotFoundError(f"Product with ID {product_id} not found.")

            return Product.model_validate(data)
        except FakeStoreItemNotFoundError:
            raise
        except httpx.HTTPStatusError as exc:
            logger.error("FakeStore API HTTP error on /products/%d: status=%d", product_id, exc.response.status_code)
            raise FakeStoreUpstreamError(
                f"FakeStore API error: {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("FakeStore API connection failure on /products/%d: %s", product_id, exc)
            raise FakeStoreUpstreamError("Failed to reach FakeStore API upstream service") from exc

    async def get_categories(self) -> List[str]:
        """
        Fetch the list of all available product category labels.
        """
        try:
            response = await self._client.get("/products/categories")
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.warning("Unexpected response format from FakeStore /products/categories: %s", type(data))
                return []
            return [str(cat) for cat in data]
        except httpx.HTTPStatusError as exc:
            logger.error("FakeStore API HTTP error on /products/categories: status=%d", exc.response.status_code)
            raise FakeStoreUpstreamError(
                f"FakeStore API error: {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("FakeStore API connection failure on /products/categories: %s", exc)
            raise FakeStoreUpstreamError("Failed to reach FakeStore API upstream service") from exc

    async def get_products_by_category(
        self,
        category: str,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
    ) -> List[Product]:
        """
        Fetch products belonging to a specific category.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if sort is not None:
            params["sort"] = sort

        try:
            response = await self._client.get(f"/products/category/{category}", params=params)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.warning("Unexpected response format from FakeStore /products/category/%s: %s", category, type(data))
                return []
            return [Product.model_validate(item) for item in data]
        except httpx.HTTPStatusError as exc:
            logger.error("FakeStore API HTTP error on /products/category/%s: status=%d", category, exc.response.status_code)
            raise FakeStoreUpstreamError(
                f"FakeStore API error: {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.error("FakeStore API connection failure on /products/category/%s: %s", category, exc)
            raise FakeStoreUpstreamError("Failed to reach FakeStore API upstream service") from exc
