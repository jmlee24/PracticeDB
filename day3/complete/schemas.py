"""
day3/complete/schemas.py — Day2 스키마 + Order 관련 (완성형)
================================================================
Day 3 의 nested Pydantic: OrderResponse 안에 items: list[OrderItemResponse].
양쪽 모두 model_config = {"from_attributes": True} 가 있어야 자동 변환된다.
"""
from pydantic import BaseModel
from datetime import datetime


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
    """
    주문 항목 생성 요청.
    클라이언트는 product_id 와 quantity 만 보낸다.
    unit_price 는 서버가 DB에서 조회해 채운다 (가격 변조 방지).
    """
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    """
    주문 생성 요청 — 한 번에 여러 항목.
    items 가 nested 리스트. Pydantic 이 자동으로 OrderItemCreate 리스트로 검증.
    """
    customer_name: str
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: int
    model_config = {"from_attributes": True}  # ← nested 변환에 필수


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    total_amount: int
    items: list[OrderItemResponse]   # ← ORM relationship 이 자동으로 직렬화됨
    created_at: datetime
    model_config = {"from_attributes": True}  # ← nested 변환에 필수
