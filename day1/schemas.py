"""
Pydantic 스키마 (API 요청/응답 형식 정의)
=========================================
ORM 모델과 API 스키마를 분리하는 이유:
→ 클라이언트가 보내는 데이터(Create)와 서버가 응답하는 데이터(Response)의 형태가 다르기 때문.
"""
from pydantic import BaseModel
from datetime import datetime

class CategoryCreate(BaseModel):
    """카테고리 생성 요청 스키마"""
    name: str
    description: str | None = None

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 3] is_active 필드 추가                      │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 타입: bool                                       │
    # │ - 기본값: True                                     │
    # │                                                    │
    # │ 힌트: is_active: bool = True                       │
    # │                                                    │
    # │ 기본값이 True이므로, 클라이언트가 이 필드를        │
    # │ 생략하면 자동으로 활성 상태로 생성됩니다.          │
    # └──────────────────────────────────────────────────┘


class CategoryResponse(BaseModel):
    """카테고리 조회 응답 스키마"""
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 4] is_active 필드 추가                      │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 타입: bool                                       │
    # │                                                    │
    # │ 힌트: is_active: bool                              │
    # │                                                    │
    # │ Response에는 기본값이 필요 없습니다.               │
    # │ DB에서 읽어온 값을 그대로 반환하면 됩니다.         │
    # └──────────────────────────────────────────────────┘

    model_config = {"from_attributes": True}
