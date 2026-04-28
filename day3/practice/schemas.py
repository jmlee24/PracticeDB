"""
day3/practice/schemas.py — Pydantic 스키마 (TODO 빈칸)
================================================================
[과제] complete 의 Order 스키마 4종을 Booking 으로 옮긴다.
"""
from pydantic import BaseModel
from datetime import datetime


class BrandCreate(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True


class BrandResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: int
    stock: int = 0
    brand_id: int


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    stock: int
    brand_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 3] BookingSeatCreate                                 │
# │                                                            │
# │ 필드(complete 의 OrderItemCreate 와 같은 구조):            │
# │ - item_id: int                                             │
# │ - seat_count: int                                          │
# │                                                            │
# │ seat_price 는 여기에 두지 않는다 (서버가 DB에서 채움).     │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 4] BookingCreate                                     │
# │                                                            │
# │ 필드:                                                      │
# │ - customer_name: str                                       │
# │ - seats: list[BookingSeatCreate]   ← nested 리스트         │
# │                                                            │
# │ 힌트: complete 의 OrderCreate 패턴 (items → seats)         │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 5] BookingSeatResponse                               │
# │                                                            │
# │ 필드:                                                      │
# │ - id: int                                                  │
# │ - item_id: int                                             │
# │ - seat_count: int                                          │
# │ - seat_price: int                                          │
# │ - model_config = {"from_attributes": True}                 │
# │                                                            │
# │ 함정: from_attributes 가 없으면 nested 변환 실패!          │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 6] BookingResponse                                   │
# │                                                            │
# │ 필드:                                                      │
# │ - id: int                                                  │
# │ - customer_name: str                                       │
# │ - status: str                                              │
# │ - total_price: int                                         │
# │ - seats: list[BookingSeatResponse]   ← 이게 핵심 nested    │
# │ - created_at: datetime                                     │
# │ - model_config = {"from_attributes": True}                 │
# └──────────────────────────────────────────────────────────┘
