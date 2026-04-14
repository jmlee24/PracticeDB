"""
Pydantic 스키마 (API 요청/응답 형식 정의)
=========================================
Day 4 완성본 + MES 도메인 신규 스키마 (Process, BOMEntry).

핵심 개념:
- 입력(Create)과 출력(Response)을 분리 — 클라이언트가 보내는 필드 ≠ 서버가 돌려주는 필드
- from_attributes=True — ORM 객체를 Pydantic 모델로 직렬화할 때 필요
- material_name — relationship 객체에서 꺼낸 값을 API 레이어에서 수동 주입
"""
from pydantic import BaseModel
from datetime import datetime


# ============================================================
# Category 스키마 — Day 4 완성본
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
# Product 스키마 — Day 4 완성본
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
# Order 스키마 — Day 4 완성본
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
# 페이지네이션 스키마 — Day 4 완성본
# ============================================================

class PaginatedResponse(BaseModel):
    """페이지네이션 응답 스키마 — 어떤 items 타입에도 재사용 가능"""
    total: int
    page: int
    size: int
    items: list


# ============================================================
# Process 스키마 — Day 6 신규
# ============================================================

# ┌──────────────────────────────────────────────────┐
# │ [TODO 45] ProcessCreate (★☆☆)                    │
# │                                                    │
# │ 공정 생성 요청 스키마.                             │
# │                                                    │
# │ 필드:                                              │
# │ - name: str                                        │
# │ - description: str | None = None                  │
# │ - sequence_order: int                              │
# │ - parent_id: int | None = None                    │
# │   → None이면 최상위 공정                           │
# └──────────────────────────────────────────────────┘
class ProcessCreate(BaseModel):
    """공정 생성 요청 스키마"""
    name: str
    description: str | None = None
    sequence_order: int
    parent_id: int | None = None


# ┌──────────────────────────────────────────────────┐
# │ [TODO 46] ProcessResponse (★★☆)                  │
# │                                                    │
# │ 공정 조회 응답 스키마.                             │
# │                                                    │
# │ 필드:                                              │
# │ - id, name, description                            │
# │ - sequence_order: int                              │
# │ - parent_id: int | None — 최상위 공정은 None       │
# │ - is_active: bool                                  │
# │ - created_at: datetime                             │
# │                                                    │
# │ model_config = {"from_attributes": True}           │
# └──────────────────────────────────────────────────┘
class ProcessResponse(BaseModel):
    """공정 조회 응답 스키마"""
    id: int
    name: str
    description: str | None = None
    sequence_order: int
    parent_id: int | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# BOMEntry 스키마 — Day 6 신규
# ============================================================

# ┌──────────────────────────────────────────────────┐
# │ [TODO 47] BOMEntryCreate (★☆☆)                   │
# │                                                    │
# │ BOM 항목 생성 요청 스키마.                         │
# │                                                    │
# │ 필드:                                              │
# │ - product_id: int  (완제품 id)                    │
# │ - material_id: int (자재 id)                      │
# │ - quantity: float                                  │
# │ - unit: str = "ea"                                │
# └──────────────────────────────────────────────────┘
class BOMEntryCreate(BaseModel):
    """BOM 항목 생성 요청 스키마"""
    product_id: int
    material_id: int
    quantity: float
    unit: str = "ea"


# ┌──────────────────────────────────────────────────┐
# │ [TODO 48] BOMEntryResponse (★★☆)                 │
# │                                                    │
# │ BOM 항목 조회 응답 스키마.                         │
# │                                                    │
# │ 필드:                                              │
# │ - id, product_id, material_id                      │
# │ - material_name: str — 자재 이름 (API에서 수동 주입)│
# │ - quantity: float                                  │
# │ - unit: str                                        │
# │                                                    │
# │ material_name은 ORM 객체에 없는 필드이므로         │
# │ 라우트에서 BOMEntryResponse(                       │
# │   **entry.__dict__, material_name=entry.material.name│
# │ ) 형태로 수동 설정합니다.                          │
# └──────────────────────────────────────────────────┘
class BOMEntryResponse(BaseModel):
    """BOM 항목 조회 응답 스키마 — material_name은 API 레이어에서 수동 주입"""
    id: int
    product_id: int
    material_id: int
    material_name: str
    quantity: float
    unit: str

    model_config = {"from_attributes": True}
