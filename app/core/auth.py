"""
Authentication Adapter (Inbound / Web).

This file contains all the authentication logic for extracting and validating
credentials from HTTP requests and converting them into a trusted SecurityContext.
"""

from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import SecurityContext, Role
from app.core.exceptions import AuthenticationException


# 1. FastAPI Security scheme: Displays the 'Authorize' button in Swagger UI (/docs)
bearer_scheme = HTTPBearer(auto_error=False)

# Standard password for all users
DEFAULT_USER_PASSWORD = "123456"

# 2. In-Memory Toy Token Registry & User Credentials
TOY_TOKENS: dict[str, dict] = {
    "token-business-49": {
        "user_id": "User_49",
        "username": "user49",
        "password": DEFAULT_USER_PASSWORD,
        "role": Role.BUSINESS,
    },
    "token-admin-01": {
        "user_id": "Admin_01",
        "username": "admin",
        "password": DEFAULT_USER_PASSWORD,
        "role": Role.ADMIN,
    },
}


def authenticate_credentials(username: str, password: str) -> dict:
    """Validate username and password, returning token and user metadata."""
    clean_username = username.strip().lower()
    for token, user_data in TOY_TOKENS.items():
        if (
            user_data["username"].lower() == clean_username
            or user_data["user_id"].lower() == clean_username
        ):
            if password == user_data["password"]:
                return {
                    "token": token,
                    "user_id": user_data["user_id"],
                    "role": user_data["role"].value,
                }
            raise AuthenticationException("Invalid password. Please enter 123456.")

    raise AuthenticationException(f"Unknown user '{username}'. Available users: user49, admin")


def authenticate_token(token: str) -> SecurityContext:
    user_info = TOY_TOKENS.get(token)
    if not user_info:
        raise AuthenticationException("Invalid or expired authentication token.")

    # REST requests are triggered directly by human
    return SecurityContext(
        user_id=user_info["user_id"],
        role=user_info["role"],
        actor="human",
    )


async def get_current_security_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> SecurityContext:
    if not credentials or not credentials.credentials:
        raise AuthenticationException(
            "Authorization header missing. Please provide a Bearer token (e.g. 'token-business-49' or 'token-admin-01')."
        )

    return authenticate_token(credentials.credentials)
