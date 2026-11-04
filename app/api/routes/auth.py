from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.auth import authenticate_credentials, get_current_security_context
from app.core.security import SecurityContext

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    return authenticate_credentials(username=request.username, password=request.password)


@router.get("/me")
async def get_me(
    context: Annotated[SecurityContext, Depends(get_current_security_context)]
):
    return {
        "user_id": context.user_id,
        "role": context.role.value,
        "actor": context.actor,
    }
