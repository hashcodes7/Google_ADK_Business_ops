from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.auth import get_current_security_context
from app.core.security import SecurityContext
from app.services.product_service import product_service
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
async def get_products(
    context: Annotated[SecurityContext, Depends(get_current_security_context)]
):
    return product_service.get_all_products(context=context)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    context: Annotated[SecurityContext, Depends(get_current_security_context)]
):
    return product_service.get_product(product_id=product_id, context=context)


@router.get("/category/{category}", response_model=list[ProductResponse])
async def get_products_by_category(
    category: str,
    context: Annotated[SecurityContext, Depends(get_current_security_context)]
):
    return product_service.get_products_by_category(category=category, context=context)


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    context: Annotated[SecurityContext, Depends(get_current_security_context)]
):
    return product_service.create_product(
        title=product.title,
        price=product.price,
        description=product.description,
        category=product.category,
        image=product.image,
        context=context,
    )
