"""day7/complete/schemas.py — Day6 + WorkOrder 스키마."""
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
    id: int
    product_id: int
    material_id: int
    material_name: str
    quantity: float
    unit: str
    model_config = {"from_attributes": True}


class WorkOrderCreate(BaseModel):
    """작업지시 생성. order_number 는 서버가 자동 생성하므로 빠짐."""
    product_id: int
    process_id: int
    quantity: int


class WorkOrderItemResponse(BaseModel):
    id: int
    material_id: int
    material_name: str   # 계산 필드
    required_qty: float
    consumed_qty: float
    model_config = {"from_attributes": True}


class WorkOrderResponse(BaseModel):
    id: int
    order_number: str
    product_id: int
    process_id: int
    quantity: int
    status: str
    items: list[WorkOrderItemResponse]
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    model_config = {"from_attributes": True}


class ConsumeRequest(BaseModel):
    """실적 등록: 어떤 자재를 얼마 소비했는지."""
    material_id: int
    consumed_qty: float
