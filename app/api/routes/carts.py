from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.auth import get_current_security_context
from app.core.security import SecurityContext
from app.services.cart_service import cart_service

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("/")
async def get_carts(
    context: Annotated[SecurityContext, Depends(get_current_security_context)]
):
    return cart_service.get_all_carts(context=context)
