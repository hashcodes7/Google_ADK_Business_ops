from pydantic import BaseModel, Field


class CartItem(BaseModel):
    productId: int
    quantity: int = Field(ge=1)


class CartResponse(BaseModel):
    id: int
    userId: int
    date: str
    products: list[CartItem]
