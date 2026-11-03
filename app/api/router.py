from fastapi import APIRouter
from app.api.routes import products, carts

api_router = APIRouter()

api_router.include_router(products.router)
api_router.include_router(carts.router)


@api_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "business-dashboard"}