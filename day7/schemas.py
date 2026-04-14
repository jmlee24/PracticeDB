"""
Pydantic 스키마 (API 요청/응답 형식 정의)
=========================================
Day 6 완성본 — Category, Product, Order, OrderItem, Process, BOMEntry 스키마 완성.
Day 7 추가 — WorkOrderCreate, WorkOrderItemResponse, WorkOrderResponse.

핵심 개념:
- 입력(Create)과 출력(Response)을 분리: 클라이언트가 보내는 데이터와
  서버가 돌려주는 데이터의 형태가 다르기 때문
- order_number는 서버에서 자동 생성하므로 Create 스키마에 포함하지 않음
- started_at / completed_at 은 작업 시작/완료 전엔 None이므로 Optional
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


# ============================================================
# Process 스키마
# ============================================================

class ProcessCreate(BaseModel):
    """공정 생성 요청 스키마"""
    name: str
    description: str | None = None
    parent_id: int | None = None


class ProcessResponse(BaseModel):
    """공정 조회 응답 스키마"""
    id: int
    name: str
    description: str | None = None
    parent_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# BOM 스키마
# ============================================================

class BOMEntryCreate(BaseModel):
    """BOM 항목 생성 요청 스키마"""
    product_id: int
    material_id: int
    quantity: float


class BOMEntryResponse(BaseModel):
    """BOM 항목 조회 응답 스키마"""
    id: int
    product_id: int
    material_id: int
    quantity: float

    model_config = {"from_attributes": True}


# ============================================================
# WorkOrder 스키마 — Day 7 신규
# ============================================================

# ┌──────────────────────────────────────────────────┐
# │ [TODO 57] WorkOrderCreate 스키마 (★★☆)            │
# │                                                    │
# │ 클라이언트가 작업지시 생성 시 보내는 필드:          │
# │ - product_id: int — 만들 완제품 ID                 │
# │ - process_id: int — 사용할 공정 ID                 │
# │ - quantity: int — 생산 목표 수량                   │
# │                                                    │
# │ order_number는 서버에서 자동 생성하므로             │
# │ 클라이언트가 보내지 않아도 됩니다.                  │
# └──────────────────────────────────────────────────┘
class WorkOrderCreate(BaseModel):
    """작업지시 생성 요청 스키마 — order_number는 서버 자동 생성"""
    product_id: int
    process_id: int
    quantity: int


# ┌──────────────────────────────────────────────────┐
# │ [TODO 58] WorkOrderItemResponse +                  │
# │           WorkOrderResponse 스키마 (★★☆)          │
# │                                                    │
# │ WorkOrderItemResponse:                             │
# │ - id: int                                          │
# │ - material_id: int                                 │
# │ - material_name: str — 자재 이름 (조회 편의)       │
# │ - required_qty: float — BOM 기준 필요량            │
# │ - consumed_qty: float — 실제 소비량                │
# │                                                    │
# │ WorkOrderResponse:                                 │
# │ - id, order_number, product_id, process_id,        │
# │   quantity, status                                 │
# │ - items: list[WorkOrderItemResponse]               │
# │ - created_at: datetime                             │
# │ - started_at: datetime | None — 미시작이면 None    │
# │ - completed_at: datetime | None — 미완료이면 None  │
# └──────────────────────────────────────────────────┘
class WorkOrderItemResponse(BaseModel):
    """작업지시 소요자재 조회 응답 스키마"""
    id: int
    material_id: int
    material_name: str   # 자재명 — 프론트엔드 표시 편의를 위해 포함
    required_qty: float
    consumed_qty: float

    model_config = {"from_attributes": True}


class WorkOrderResponse(BaseModel):
    """작업지시 조회 응답 스키마"""
    id: int
    order_number: str
    product_id: int
    process_id: int
    quantity: int
    status: str
    items: list[WorkOrderItemResponse]
    created_at: datetime
    started_at: datetime | None    # 아직 시작 전이면 None
    completed_at: datetime | None  # 아직 완료 전이면 None

    model_config = {"from_attributes": True}
