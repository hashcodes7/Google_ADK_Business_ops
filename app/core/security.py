import os
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

from app.core.exceptions import UnauthorizedException


ActorType = Literal["human", "agent"]


class SecurityContext(BaseModel):
    user_id: str = Field(default_factory=lambda: os.getenv("AUTH_USER_ID", "User_49"))
    role: str = Field(default_factory=lambda: os.getenv("AUTH_ROLE", "Business"))
    actor: ActorType = "human"


def create_security_context(actor: ActorType = "human") -> SecurityContext:
    """Creates a trusted SecurityContext for inbound adapters."""
    return SecurityContext(
        user_id=os.getenv("AUTH_USER_ID", "User_49"),
        role=os.getenv("AUTH_ROLE", "Business"),
        actor=actor,
    )


def require_permission(context: SecurityContext, allowed_actors: list[ActorType] | None = None, required_role: str | None = None) -> None:
    """Centralized authorization check across inbound adapters."""
    if allowed_actors and context.actor not in allowed_actors:
        raise UnauthorizedException(f"Operation denied for actor '{context.actor}'. Allowed: {allowed_actors}")
    if required_role and context.role != required_role:
        raise UnauthorizedException(f"Operation denied for role '{context.role}'. Required: {required_role}")
