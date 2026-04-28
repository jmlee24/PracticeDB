"""day6/practice/schemas.py — Day5 + Department/Recipe 스키마 TODO."""
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
# │ [TODO 3] DepartmentCreate                                  │
# │                                                            │
# │ 필드:                                                      │
# │ - name: str                                                │
# │ - description: str | None = None                           │
# │ - parent_id: int | None = None  (미전달 → 최상위 부서)     │
# │                                                            │
# │ 힌트: complete 의 ProcessCreate 와 같은 구조.              │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 4] DepartmentResponse                                │
# │                                                            │
# │ - id: int                                                  │
# │ - name: str                                                │
# │ - description: str | None                                  │
# │ - parent_id: int | None                                    │
# │ - created_at: datetime                                     │
# │ - model_config = {"from_attributes": True}                 │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 5] RecipeCreate                                      │
# │ - product_id: int                                          │
# │ - material_id: int                                         │
# │ - quantity: float                                          │
# │ - unit: str = "ea"                                         │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 6] RecipeResponse                                    │
# │                                                            │
# │ - id: int                                                  │
# │ - product_id: int                                          │
# │ - material_id: int                                         │
# │ - material_name: str  ← 모델에 없음! 라우트에서 채움       │
# │ - quantity: float                                          │
# │ - unit: str                                                │
# │ - model_config = {"from_attributes": True}                 │
# │                                                            │
# │ 힌트: complete 의 BOMEntryResponse 와 같은 패턴.           │
# └──────────────────────────────────────────────────────────┘


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[Any]
