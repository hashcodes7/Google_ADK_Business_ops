from typing import Any, Protocol


class EcommercePort(Protocol):
    """Outbound port for e-commerce catalog, cart, and user operations."""

    def get_all_products(self) -> list[dict[str, Any]]:
        ...

    def get_product(self, product_id: int) -> dict[str, Any]:
        ...

    def get_products_by_category(self, category: str) -> list[dict[str, Any]]:
        ...

    def create_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        ...

    def get_all_carts(self) -> list[dict[str, Any]]:
        ...

    def get_cart_by_id(self, cart_id: int) -> dict[str, Any]:
        ...

    def get_all_users(self) -> list[dict[str, Any]]:
        ...

    def create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        ...
