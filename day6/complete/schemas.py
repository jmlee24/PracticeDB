"""day6/complete/schemas.py — Day5 + Process/BOM 스키마 추가."""
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


class ProcessCreate(BaseModel):
    """공정 생성. parent_id 미전달 → 최상위."""
    name: str
    description: str | None = None
    parent_id: int | None = None


class ProcessResponse(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int | None
    created_at: datetime
    model_config = {"from_attributes": True}


class BOMEntryCreate(BaseModel):
    product_id: int
    material_id: int
    quantity: float
    unit: str = "ea"


class BOMEntryResponse(BaseModel):
    """
    BOM 응답.
    material_name 은 BOMEntry 모델에 없는 '계산 필드'.
    라우트에서 entry.material.name 으로 끌어와 수동 주입.
    """
    id: int
    product_id: int
    material_id: int
    material_name: str   # ← 모델에 없음. 라우트에서 채움.
    quantity: float
    unit: str
    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[Any]
