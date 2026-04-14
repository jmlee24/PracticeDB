"""
SQLAlchemy 모델 (DB 테이블 정의)
================================
ORM(Object-Relational Mapping)은 파이썬 클래스를 DB 테이블에 매핑합니다.

이 파일의 Category 모델을 읽고 이해한 뒤, TODO를 풀어보세요.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from day1.database import Base

class Category(Base):
    """카테고리 테이블"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 2] is_active 컬럼 추가                      │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 타입: Boolean                                    │
    # │ - NULL 불가                                        │
    # │ - 기본값: True                                     │
    # │                                                    │
    # │ 힌트: Column(Boolean, nullable=False, default=True)│
    # │                                                    │
    # │ 이 필드는 "카테고리 비활성화" 기능에 사용됩니다.   │
    # │ 삭제 대신 is_active=False로 비활성화하는 패턴을    │
    # │ "소프트 삭제(soft delete)"라고 합니다.             │
    # └──────────────────────────────────────────────────┘
