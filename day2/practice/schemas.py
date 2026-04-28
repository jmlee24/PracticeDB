"""
day2/practice/schemas.py — Pydantic 스키마 (TODO 빈칸)
================================================================
참고: day2/complete/schemas.py 의 ProductCreate / ProductResponse.
이름만 바꾸면 끝난다.
"""
from pydantic import BaseModel
from datetime import datetime


class BrandCreate(BaseModel):
    """브랜드 생성 — Day 1 CategoryCreate 와 동일 구조."""
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
    """
    상품 생성 요청.
    """
    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 4] ItemCreate 의 5개 필드 추가                   │
    # │                                                        │
    # │ 필드(complete 의 ProductCreate 와 같은 구조):          │
    # │ - name: str               (필수)                       │
    # │ - description: str | None = None                       │
    # │ - price: int              (필수)                       │
    # │ - stock: int = 0                                       │
    # │ - brand_id: int           (필수, FK)                   │
    # └──────────────────────────────────────────────────────┘


class ItemResponse(BaseModel):
    """
    상품 응답.
    """
    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 5] ItemResponse 의 8개 필드 + model_config       │
    # │                                                        │
    # │ 필드:                                                  │
    # │ - id: int                                              │
    # │ - name: str                                            │
    # │ - description: str | None                              │
    # │ - price: int                                           │
    # │ - stock: int                                           │
    # │ - brand_id: int                                        │
    # │ - created_at: datetime                                 │
    # │ - updated_at: datetime                                 │
    # │ - model_config = {"from_attributes": True}             │
    # └──────────────────────────────────────────────────────┘
