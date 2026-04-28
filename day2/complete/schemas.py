"""
day2/complete/schemas.py — Pydantic 스키마 (완성형)
================================================================
4개 스키마: Category Create/Response + Product Create/Response.
"""
from pydantic import BaseModel
from datetime import datetime


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
    """상품 생성 요청."""
    name: str
    description: str | None = None
    price: int                # 필수. 0 이상 같은 검증은 라우트에서.
    stock: int = 0            # 선택. 미전달 시 0.
    category_id: int          # 필수. 라우트가 존재하는 ID인지 검증한다.


class ProductResponse(BaseModel):
    """상품 응답 — DB의 모든 필드 노출."""
    id: int
    name: str
    description: str | None
    price: int
    stock: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
