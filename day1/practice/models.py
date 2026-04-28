"""
day1/practice/models.py — Category 모델 (TODO 빈칸 문제)
================================================================
[과제] 노출 토글 패턴
    complete 에서는 'is_active' (기본값 True, 활성/비활성) 패턴을 봤다.
    여기서는 약간 다르게:
        - 컬럼명: is_published
        - 의미:   "공개 여부"
        - 기본값: False  ← 주의! 작성자가 명시적으로 공개해야만 노출됨

같은 패턴(Boolean + nullable + default) 을 다른 의미로 적용하는 연습.
참고: day1/complete/models.py 의 Category.is_active 정의 라인.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime, timezone

from day1.practice.database import Base


class Category(Base):
    """카테고리 테이블 — 노출 토글(is_published) 변형."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 1] is_published 컬럼 추가                        │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 타입: Boolean                                        │
    # │ - NULL 불가                                            │
    # │ - 기본값: False  ← complete의 is_active 와 반대!       │
    # │                                                        │
    # │ 힌트: day1/complete/models.py 의 is_active 라인을 보고 │
    # │       default 값만 False 로 바꾸면 된다.               │
    # └──────────────────────────────────────────────────────┘

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
