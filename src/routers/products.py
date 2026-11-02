from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from src.clients.fakestore_client import (
    FakeStoreClient,
    FakeStoreItemNotFoundError,
    FakeStoreUpstreamError,
)
from src.dependencies import get_fakestore_client
from src.schemas.product import Product

router = APIRouter(
    prefix="/products",
    tags=["Products & Categories"],
)


@router.get(
    "",
    response_model=List[Product],
    summary="List all products",
    description="Fetch a catalog of products from FakeStore with optional result limit and sorting order.",
)
async def list_products(
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of products to return",
        examples=[5],
    ),
    sort: Optional[Literal["asc", "desc"]] = Query(
        default=None,
        description="Sort ordering direction by product ID ('asc' or 'desc')",
        examples=["desc"],
    ),
    client: FakeStoreClient = Depends(get_fakestore_client),
) -> List[Product]:
    try:
        return await client.get_products(limit=limit, sort=sort)
    except FakeStoreUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/categories",
    response_model=List[str],
    summary="List all product categories",
    description="Fetch distinct product categories available across the store catalog.",
)
async def list_categories(
    client: FakeStoreClient = Depends(get_fakestore_client),
) -> List[str]:
    try:
        return await client.get_categories()
    except FakeStoreUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/category/{category_name}",
    response_model=List[Product],
    summary="List products in a specific category",
    description="Fetch all products belonging to a given category name (e.g. 'electronics', 'jewelery').",
)
async def list_products_by_category(
    category_name: str = Path(
        ...,
        min_length=1,
        description="Category name to filter products by",
        examples=["electronics"],
    ),
    limit: Optional[int] = Query(
        default=None,
        ge=1,
        le=100,
        description="Maximum number of products to return",
    ),
    sort: Optional[Literal["asc", "desc"]] = Query(
        default=None,
        description="Sort ordering direction ('asc' or 'desc')",
    ),
    client: FakeStoreClient = Depends(get_fakestore_client),
) -> List[Product]:
    try:
        return await client.get_products_by_category(
            category=category_name,
            limit=limit,
            sort=sort,
        )
    except FakeStoreUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{product_id}",
    response_model=Product,
    summary="Get single product by ID",
    description="Fetch full details for an individual product by its numeric ID.",
    responses={
        404: {"description": "Product not found"},
    },
)
async def get_product(
    product_id: int = Path(
        ...,
        ge=1,
        description="Unique identifier of the target product",
        examples=[1],
    ),
    client: FakeStoreClient = Depends(get_fakestore_client),
) -> Product:
    try:
        return await client.get_product(product_id=product_id)
    except FakeStoreItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except FakeStoreUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
