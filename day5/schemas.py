"""
Pydantic 스키마 (API 요청/응답 형식 정의)
=========================================
Day 4 완성본 — Category, Product, Order, OrderItem 스키마 모두 완성.

핵심 개념:
- nested 스키마: OrderResponse 안에 OrderItemResponse 리스트를 품는 구조
  → from_attributes=True 덕분에 ORM relationship도 자동 직렬화됨
- 입력(Create)과 출력(Response)을 분리하는 이유:
  클라이언트가 보내는 데이터와 서버가 돌려주는 데이터의 형태가 다르기 때문
"""
from pydantic import BaseModel
from datetime import datetime


# ============================================================
# Category 스키마
# ============================================================

class CategoryCreate(BaseModel):
    """카테고리 생성 요청 스키마"""
    name: str
    description: str | None = None
    is_active: bool = True


class CategoryResponse(BaseModel):
    """카테고리 조회 응답 스키마"""
    id: int
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Product 스키마
# ============================================================

class ProductCreate(BaseModel):
    """상품 생성 요청 스키마"""
    name: str
    description: str | None = None
    price: int
    stock: int = 0
    category_id: int


class ProductResponse(BaseModel):
    """상품 조회 응답 스키마"""
    id: int
    name: str
    description: str | None = None
    price: int
    stock: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Order 스키마
# ============================================================

class OrderItemCreate(BaseModel):
    """주문 항목 생성 요청 스키마"""
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    """주문 생성 요청 스키마"""
    customer_name: str
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    """주문 항목 조회 응답 스키마"""
    id: int
    product_id: int
    quantity: int
    unit_price: int

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """주문 조회 응답 스키마"""
    id: int
    customer_name: str
    status: str
    total_amount: int
    items: list[OrderItemResponse]
    created_at: datetime

    model_config = {"from_attributes": True}
