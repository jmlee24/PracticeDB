"""
day5/complete/models.py — Day4 + 인덱스/유니크 제약 (완성형, 줄단위 해설)
================================================================
Day 5 신규:
    1) index=True       — 단일 컬럼 인덱스 (B-Tree, O(log n) 탐색)
    2) Index("이름", "col1", "col2")  — 복합 인덱스
    3) UniqueConstraint("c1","c2", name="...")  — 복합 유니크 제약
    4) __table_args__   — 테이블 수준 제약을 튜플로 묶어 선언

이 파일을 변경하면 alembic revision --autogenerate 가 변경을 감지해
마이그레이션 파일을 만든다.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey,
    Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day5.complete.database import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # index=True → CREATE INDEX ix_products_name ON products(name)
    # 효과: WHERE name = '...' / WHERE name ILIKE '...' 속도 ↑
    name = Column(String(200), nullable=False, index=True)

    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category = relationship("Category", back_populates="products")

    # __table_args__ 는 반드시 튜플. 항목 1개여도 끝에 콤마(,) 필수.
    # UniqueConstraint("name", "category_id") → 같은 카테고리 안에서 이름 중복 금지.
    # 즉 다른 카테고리에는 같은 이름 허용 (실무 패턴).
    __table_args__ = (
        UniqueConstraint("name", "category_id", name="uq_product_name_category"),
    )


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)

    # status 별 조회는 매우 잦음 → 인덱스 효과 큼.
    # 카디널리티(고유값 종류)가 낮아도(pending/cancelled 정도) 인덱스가 유효한 경우가 많다.
    status = Column(String(20), nullable=False, default="pending", index=True)

    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    items = relationship("OrderItem", back_populates="order")

    # 복합 인덱스: WHERE customer_name = ? AND created_at > ? 같은 쿼리 최적화.
    # "단일 인덱스 두 개" 보다 "복합 인덱스 한 개" 가 더 효율적인 경우가 많다.
    __table_args__ = (
        Index("ix_orders_customer_created", "customer_name", "created_at"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
