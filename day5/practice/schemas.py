"""day5/practice/schemas.py — Day4 practice + ItemCreate/Response 에 barcode 추가 (TODO)"""
from pydantic import BaseModel
from datetime import datetime
from typing import Any


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

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 6] barcode 필드 추가                              │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 타입: str | None                                     │
    # │ - 기본값: None (선택 입력)                             │
    # │                                                        │
    # │ 힌트: barcode: str | None = None                       │
    # └──────────────────────────────────────────────────────┘


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    stock: int
    brand_id: int
    created_at: datetime
    updated_at: datetime
    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 7] barcode 필드 추가 (Response)                  │
    # │ - barcode: str | None                                  │
    # └──────────────────────────────────────────────────────┘
    model_config = {"from_attributes": True}


class BookingSeatCreate(BaseModel):
    item_id: int
    seat_count: int


class BookingCreate(BaseModel):
    customer_name: str
    seats: list[BookingSeatCreate]


class BookingSeatResponse(BaseModel):
    id: int
    item_id: int
    seat_count: int
    seat_price: int
    model_config = {"from_attributes": True}


class BookingResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    total_price: int
    seats: list[BookingSeatResponse]
    created_at: datetime
    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[Any]
