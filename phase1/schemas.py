"""
Pydantic 스키마 (API 요청/응답 형식 정의)
=========================================
ORM 모델 ≠ API 스키마

- ORM 모델 (models.py): DB 테이블과 1:1 매핑
- Pydantic 스키마 (이 파일): API에서 주고받는 데이터의 형태를 정의

왜 분리하는가?
→ DB에는 created_at, updated_at 같은 내부 필드가 있지만
  클라이언트가 상품을 생성할 때는 name, price만 보내면 됨.
  입력(Create)과 출력(Response)의 형태가 다르기 때문에 분리.

문제가 포함되어 있습니다. [TODO] 주석을 찾아 코드를 완성하세요.
"""

from pydantic import BaseModel
from datetime import datetime


# ============================================================
# Category 스키마 (완성 - 참고용)
# ============================================================

class CategoryCreate(BaseModel):
    """카테고리 생성 요청 시 클라이언트가 보내는 데이터"""
    name: str
    description: str | None = None


class CategoryResponse(BaseModel):
    """카테고리 조회 응답 시 클라이언트에 보내는 데이터"""
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
    # from_attributes=True: ORM 객체를 자동으로 이 스키마로 변환해줌
    # 예: CategoryResponse.model_validate(category_orm_object)


# ============================================================
# Product 스키마 (TODO 포함)
# ============================================================

class ProductCreate(BaseModel):
    """
    상품 생성 요청 스키마

    클라이언트가 POST /products 로 보내는 JSON 형태:
    {
        "name": "볼트 M8",
        "description": "8mm 육각볼트",
        "price": 500,
        "stock": 100,
        "category_id": 1
    }
    """
    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 5] 필드 5개를 정의하세요                     │
    # │                                                    │
    # │ 필요한 필드:                                       │
    # │ - name: str (필수)                                 │
    # │ - description: str | None, 기본값 None             │
    # │ - price: int (필수)                                │
    # │ - stock: int, 기본값 0                             │
    # │ - category_id: int (필수)                          │
    # │                                                    │
    # │ 힌트: CategoryCreate를 참고하세요                  │
    # └──────────────────────────────────────────────────┘
    pass  # ← 이 줄을 지우고 필드를 작성하세요


class ProductResponse(BaseModel):
    """
    상품 조회 응답 스키마

    GET /products 응답 JSON 형태:
    {
        "id": 1,
        "name": "볼트 M8",
        "description": "8mm 육각볼트",
        "price": 500,
        "stock": 100,
        "category_id": 1,
        "created_at": "2026-04-14T12:00:00",
        "updated_at": "2026-04-14T12:00:00"
    }
    """
    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 6] 응답 필드 8개를 정의하세요                │
    # │                                                    │
    # │ 필요한 필드:                                       │
    # │ - id: int                                          │
    # │ - name: str                                        │
    # │ - description: str | None                          │
    # │ - price: int                                       │
    # │ - stock: int                                       │
    # │ - category_id: int                                 │
    # │ - created_at: datetime                             │
    # │ - updated_at: datetime                             │
    # │                                                    │
    # │ 그리고 model_config도 설정하세요!                  │
    # │ 힌트: CategoryResponse를 참고                      │
    # └──────────────────────────────────────────────────┘
    pass  # ← 이 줄을 지우고 필드를 작성하세요
