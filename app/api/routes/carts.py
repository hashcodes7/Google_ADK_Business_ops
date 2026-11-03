from fastapi import APIRouter
from app.services import cart_service

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.get("/")
async def get_carts():
    return cart_service.get_all_carts()
