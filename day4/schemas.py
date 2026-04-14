"""
Pydantic 스키마 (API 요청/응답 형식 정의)
=========================================
Day 3 완성본 위에 페이지네이션 응답 스키마를 추가합니다.

핵심 개념:
- nested 스키마: OrderResponse 안에 OrderItemResponse 리스트를 품는 구조
- PaginatedResponse: 전체 건수 + 현재 페이지 정보 + 결과 목록을 함께 반환
- 입력(Create)과 출력(Response)을 분리하는 이유:
  클라이언트가 보내는 데이터와 서버가 돌려주는 데이터의 형태가 다르기 때문
"""
from pydantic import BaseModel
from datetime import datetime


# ============================================================
# Category 스키마 — Day 3 완성본
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
# Product 스키마 — Day 3 완성본
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
# Order 스키마 — Day 3 완성본
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


# ============================================================
# 페이지네이션 스키마 — Day 4 신규
# ============================================================

# ┌──────────────────────────────────────────────────┐
# │ [TODO 27] PaginatedResponse 스키마 정의            │
# │                                                    │
# │ 조건:                                              │
# │ - total: int (전체 건수)                           │
# │ - page: int (현재 페이지)                          │
# │ - size: int (페이지당 건수)                        │
# │ - items: list (결과 목록)                          │
# │                                                    │
# │ 사용 예시:                                         │
# │ {"total": 25, "page": 1, "size": 10, "items": [...]}│
# │                                                    │
# │ 힌트: class PaginatedResponse(BaseModel):          │
# │           total: int                               │
# │           page: int                                │
# │           size: int                                │
# │           items: list                              │
# └──────────────────────────────────────────────────┘
class PaginatedResponse(BaseModel):
    """페이지네이션 응답 스키마 — 어떤 items 타입에도 재사용 가능"""
    total: int
    page: int
    size: int
    items: list
