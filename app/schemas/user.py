from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="Username")
    email: str = Field(description="User email address")
    password: str = Field(min_length=6, description="Password")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
