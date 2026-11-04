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


# 2. In-Memory Toy Token Registry
TOY_TOKENS: dict[str, dict] = {
    "token-business-49": {
        "user_id": "User_49",
        "role": Role.BUSINESS,
    },
    "token-admin-01": {
        "user_id": "Admin_01",
        "role": Role.ADMIN,
    },
}


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
