"""
SQLAlchemy 모델 (DB 테이블 정의)
================================
ORM(Object-Relational Mapping)은 파이썬 클래스를 DB 테이블에 매핑합니다.
클래스 하나 = 테이블 하나, 인스턴스 하나 = 행(row) 하나.

이 파일의 Category 모델(완성)을 읽고 이해한 뒤, Product의 TODO를 풀어보세요.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day2.database import Base


class Category(Base):
    """
    카테고리 테이블 (완성 - 참고용)
    ─────────────────────────────
    이 모델을 참고해서 아래 Product 모델의 TODO를 풀어보세요.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # relationship: 이 카테고리에 속한 상품 목록을 가져올 수 있게 해줌
    # back_populates: Product 쪽에서도 역으로 category를 참조할 수 있게 연결
    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    상품 테이블
    ──────────
    카테고리에 속하는 상품 정보를 저장합니다.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 6] description 컬럼 추가                    │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 타입: Text                                       │
    # │ - NULL 허용                                        │
    # │                                                    │
    # │ 힌트: 위 Category 모델의 description을 참고하세요  │
    # └──────────────────────────────────────────────────┘

    price = Column(Integer, nullable=False)

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 7] stock (재고수량) 컬럼 추가                │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 타입: Integer                                    │
    # │ - NULL 불가                                        │
    # │ - 기본값: 0                                        │
    # │                                                    │
    # │ 힌트: Column(타입, nullable=?, default=?)          │
    # └──────────────────────────────────────────────────┘

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 8] category_id 외래키(FK) 컬럼 추가          │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 타입: Integer                                    │
    # │ - ForeignKey로 categories 테이블의 id를 참조       │
    # │ - NULL 불가                                        │
    # │                                                    │
    # │ 힌트: Column(Integer, ForeignKey("테이블명.컬럼"), │
    # │       nullable=False)                              │
    # └──────────────────────────────────────────────────┘

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 9] category와의 relationship 설정            │
    # │                                                    │
    # │ 조건:                                              │
    # │ - Category 모델과 연결                             │
    # │ - back_populates="products"                        │
    # │   (Category.products와 양방향 연결)                │
    # │                                                    │
    # │ 힌트: category = relationship("?",                 │
    # │       back_populates="?")                          │
    # └──────────────────────────────────────────────────┘
