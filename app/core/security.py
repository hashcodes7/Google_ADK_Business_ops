import os
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

from app.core.exceptions import UnauthorizedException


ActorType = Literal["human", "agent"]


class Role(str, Enum):
    BUSINESS = "Business"
    ADMIN = "Admin"


class Permission(str, Enum):
    PRODUCTS_READ = "products:read"
    PRODUCTS_WRITE = "products:write"
    CARTS_READ = "carts:read"
    USERS_WRITE = "users:write"


# Centralized role-to-permission mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.BUSINESS: {
        Permission.PRODUCTS_READ,
        Permission.CARTS_READ,
    },
    Role.ADMIN: {
        Permission.PRODUCTS_READ,
        Permission.CARTS_READ,
        Permission.PRODUCTS_WRITE,
        Permission.USERS_WRITE,
    },
}


class SecurityContext(BaseModel):
    user_id: str = Field(default_factory=lambda: os.getenv("AUTH_USER_ID", "User_49"))
    role: Role = Field(default_factory=lambda: Role(os.getenv("AUTH_ROLE", "Business")))
    actor: ActorType = "human"


def create_security_context(
    role: Role | str | None = None,
    user_id: str | None = None,
    actor: ActorType = "human",
) -> SecurityContext:
    """Creates a trusted SecurityContext based on Role, User ID, and Actor."""
    assigned_user = user_id or os.getenv("AUTH_USER_ID", "User_49")
    assigned_role = Role(role) if role else Role(os.getenv("AUTH_ROLE", "Business"))
    return SecurityContext(user_id=assigned_user, role=assigned_role, actor=actor)


def require_permission(context: SecurityContext, permission: Permission) -> None:
    """
    Centralized authorization guard:
    Verifies purely based on the user's Role whether the required Permission is granted.
    """
    granted_permissions = ROLE_PERMISSIONS.get(context.role, set())
    if permission not in granted_permissions:
        raise UnauthorizedException(
            f"Role '{context.role.value}' lacks required permission '{permission.value}'."
        )
