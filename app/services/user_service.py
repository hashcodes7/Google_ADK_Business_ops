from typing import Any
from app.core.exceptions import AuthenticationException
from app.core.security import SecurityContext, Permission, require_permission
from app.integrations.ecommerce_client import ecommerce_client
from app.schemas.user import UserCreate
from app.ports.ecommerce_port import EcommercePort


class UserService:
    """Application Service for user management (REST / Human Only)."""

    def __init__(self, port: EcommercePort = ecommerce_client):
        self.port = port

    def get_all_users(self, context: SecurityContext = None) -> list[dict[str, Any]]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        require_permission(context, Permission.USERS_READ)
        return self.port.get_all_users()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        context: SecurityContext = None,
    ) -> dict[str, Any]:
        if context is None:
            raise AuthenticationException("Security context is required.")
        # Only Admins can register/create new users
        require_permission(context, Permission.USERS_WRITE)

        payload = UserCreate(username=username, email=email, password=password)
        return self.port.create_user(payload.model_dump())


user_service = UserService()

def create_user(username: str, email: str, password: str, context: SecurityContext = None):
    return user_service.create_user(username=username, email=email, password=password, context=context)
