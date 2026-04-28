"""day5/complete/schemas.py — Day4 와 동일."""
from pydantic import BaseModel
from datetime import datetime
from typing import Any


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: int
    stock: int = 0
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    stock: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_name: str
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: int
    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    total_amount: int
    items: list[OrderItemResponse]
    created_at: datetime
    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[Any]
