"""
day2/practice/models.py — Brand 1:N Item (TODO 빈칸 문제)
================================================================
[과제] complete 의 Category-Product 1:N 패턴을 Brand-Item 으로 옮긴다.
       이름만 바뀌었을 뿐 구조는 동일하다 — FK + back_populates.

매핑:
    complete                practice
    -------                 --------
    Category    →    Brand
    Product     →    Item
    category_id →    brand_id
    products    →    items
    category    →    brand

참고: day2/complete/models.py 전체.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day2.practice.database import Base


class Brand(Base):
    """
    브랜드 테이블 (완성 - 참고용).
    Day 1 의 Category 와 거의 같다.
    """
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 1] items relationship 추가                       │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 연결 클래스: "Item"                                  │
    # │ - back_populates="brand"                               │
    # │                                                        │
    # │ 힌트(complete 의 Category.products 패턴):              │
    # │   items = relationship("Item", back_populates="brand") │
    # └──────────────────────────────────────────────────────┘


class Item(Base):
    """상품 테이블 — Brand 의 자식."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 2] brand_id 외래키 컬럼 추가                     │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 타입: Integer                                        │
    # │ - ForeignKey 로 brands 테이블의 id 참조                │
    # │ - NULL 불가                                            │
    # │                                                        │
    # │ 힌트(complete 의 category_id 패턴):                    │
    # │   brand_id = Column(                                   │
    # │       Integer, ForeignKey("brands.id"), nullable=False)│
    # └──────────────────────────────────────────────────────┘

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 3] brand relationship 추가                       │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 연결 클래스: "Brand"                                 │
    # │ - back_populates="items" (TODO 1 과 짝)                │
    # │                                                        │
    # │ 힌트(complete 의 Product.category 패턴):               │
    # │   brand = relationship("Brand", back_populates="items")│
    # └──────────────────────────────────────────────────────┘
