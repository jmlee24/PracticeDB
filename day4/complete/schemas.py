"""
day4/complete/schemas.py — Day3 + PaginatedResponse 추가
================================================================
Day 4 의 신규: PaginatedResponse — 모든 목록 API 의 통일된 응답 형태.
"""
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
    """
    제네릭 페이지네이션 응답.

    필드 의미:
        total: 필터 적용 후 전체 건수 (페이지네이션 적용 전!)
        page : 현재 페이지 번호 (1부터)
        size : 페이지당 건수
        items: 실제 데이터 — 라우트에서 list[ProductResponse] 등으로 채움
    """
    total: int
    page: int
    size: int
    items: list[Any]
