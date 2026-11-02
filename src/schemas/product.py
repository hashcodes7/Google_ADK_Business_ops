from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Rating(BaseModel):
    """Product review and rating metrics."""
    rate: float = Field(
        ...,
        ge=0.0,
        le=5.0,
        description="Average customer rating score (0.0 to 5.0)",
        examples=[3.9],
    )
    count: int = Field(
        ...,
        ge=0,
        description="Total count of customer ratings submitted",
        examples=[120],
    )

    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """E-commerce product entity representation from FakeStoreAPI."""
    id: int = Field(
        ...,
        ge=1,
        description="Unique product identifier",
        examples=[1],
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Title or display name of the product",
        examples=["Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops"],
    )
    price: float = Field(
        ...,
        ge=0.0,
        description="Unit price in USD",
        examples=[109.95],
    )
    description: str = Field(
        ...,
        description="Detailed product description",
        examples=["Your perfect pack for everyday use and walks in the forest."],
    )
    category: str = Field(
        ...,
        min_length=1,
        description="Product categorization classification",
        examples=["men's clothing"],
    )
    image: str = Field(
        ...,
        description="HTTP URL pointing to the product imagery asset",
        examples=["https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg"],
    )
    rating: Optional[Rating] = Field(
        default=None,
        description="Aggregate rating score and review count",
    )

    model_config = ConfigDict(from_attributes=True)
