
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    image: str = ""


class ProductResponse(ProductCreate):
    id: int
