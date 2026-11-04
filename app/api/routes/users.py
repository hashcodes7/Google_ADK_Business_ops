from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.auth import get_current_security_context
from app.core.security import SecurityContext
from app.services.user_service import user_service
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    context: Annotated[SecurityContext, Depends(get_current_security_context)],
):
    """
    User Only Endpoint:
    Provisions a new user account. Restricted to human administrators via REST.
    (Omitted from AI Agent tools).
    """
    return user_service.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        context=context,
    )
