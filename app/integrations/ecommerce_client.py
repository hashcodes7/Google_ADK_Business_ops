
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
        self.base_url = settings.ECOMMERCE_API_URL.rstrip("/")
        self.timeout = 10.0

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            logger.error(
                "E-commerce API returned HTTP %s for %s",
                exc.response.status_code,
                endpoint,
            )

            if exc.response.status_code == 404:
                raise ResourceNotFoundException(
                    "Requested e-commerce resource was not found."
                ) from exc

            raise ExternalAPIException(
                "E-commerce backend returned an error."
            ) from exc

        except httpx.RequestError as exc:
            logger.exception("E-commerce backend connection failed")

            raise ExternalAPIException(
                "Unable to connect to e-commerce backend."
            ) from exc

    def get_all_products(self):
        return self._request("GET", "/products")

    def get_product(self, product_id: int):
        return self._request("GET", f"/products/{product_id}")

    def get_products_by_category(self, category: str):
        category = quote(category, safe="")
        return self._request("GET", f"/products/category/{category}")

    def create_product(self, product_data: dict):
        return self._request(
            "POST",
            "/products",
            json=product_data,
        )

    def get_all_carts(self):
        return self._request("GET", "/carts")

    def get_cart_by_id(self, cart_id: int):
        return self._request("GET", f"/carts/{cart_id}")

    def create_user(self, user_data: dict):
        return self._request("POST", "/users", json=user_data)


ecommerce_client = EcommerceClient()
