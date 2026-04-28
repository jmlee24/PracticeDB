"""
day1/practice/schemas.py — Pydantic 스키마 (TODO 빈칸 문제)
================================================================
[과제] is_published 필드를 Create/Response 양쪽에 추가한다.
참고: day1/complete/schemas.py 의 is_active 정의 — 기본값과 의미만 다르다.
"""
from pydantic import BaseModel
from datetime import datetime


class CategoryCreate(BaseModel):
    """POST /categories 요청 본문."""
    name: str
    description: str | None = None

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 2] is_published 필드 추가                        │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 타입: bool                                           │
    # │ - 기본값: False                                        │
    # │                                                        │
    # │ 의미: 클라이언트가 생략하면 비공개 상태로 생성된다.    │
    # │      complete 의 is_active(default=True)와 정반대 정책.│
    # └──────────────────────────────────────────────────────┘


class CategoryResponse(BaseModel):
    """카테고리 조회 응답."""
    id: int
    name: str
    description: str | None
    created_at: datetime

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 3] is_published 필드 추가                        │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 타입: bool                                           │
    # │ - Response 에는 기본값이 필요 없다 (DB에서 읽어온 값). │
    # └──────────────────────────────────────────────────────┘

    model_config = {"from_attributes": True}
