from fastapi import APIRouter
from app.services import product_service
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
async def get_products():
    return product_service.get_all_products()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    return product_service.get_product(product_id)


@router.get("/category/{category}", response_model=list[ProductResponse])
async def get_products_by_category(category: str):
    return product_service.get_products_by_category(category)


@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    return product_service.create_product(**product.model_dump())
