"""day7/practice/schemas.py — Day6 practice + Shipment 스키마 TODO."""
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


class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None
    parent_id: int | None = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int | None
    created_at: datetime
    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    product_id: int
    material_id: int
    quantity: float
    unit: str = "ea"


class RecipeResponse(BaseModel):
    id: int
    product_id: int
    material_id: int
    material_name: str
    quantity: float
    unit: str
    model_config = {"from_attributes": True}


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 3] ShipmentCreate                                     │
# │ - product_id: int                                          │
# │ - department_id: int                                       │
# │ - quantity: int                                            │
# │ shipment_number 는 서버 자동 생성이므로 Create 에 없음.     │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 4] ShipmentItemResponse                               │
# │ - id: int                                                  │
# │ - material_id: int                                         │
# │ - material_name: str  ← 계산 필드                          │
# │ - required_qty: float                                      │
# │ - actual_qty: float                                        │
# │ - model_config = {"from_attributes": True}                 │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 5] ShipmentResponse                                   │
# │ - id: int                                                  │
# │ - shipment_number: str                                     │
# │ - product_id: int                                          │
# │ - department_id: int                                       │
# │ - quantity: int                                            │
# │ - status: str                                              │
# │ - items: list[ShipmentItemResponse]                        │
# │ - created_at: datetime                                     │
# │ - shipped_at: datetime | None                              │
# │ - delivered_at: datetime | None                            │
# │ - model_config = {"from_attributes": True}                 │
# └──────────────────────────────────────────────────────────┘
