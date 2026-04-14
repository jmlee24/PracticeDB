"""
SQLAlchemy 모델 (DB 테이블 정의)
================================
Day 4 완성본 + MES 도메인 신규 모델 (Process, BOMEntry).

핵심 개념:
- 자기참조 FK: 같은 테이블의 id를 parent_id로 참조 → 트리 구조 표현
- remote_side: 자기참조 relationship에서 "부모 쪽 id"를 명시
- foreign_keys: 같은 테이블을 두 번 참조할 때 어떤 FK인지 SQLAlchemy에 알림
- BOM 패턴: 완제품과 자재를 동일 테이블(Product)에서 category로 구분
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day6.database import Base


class Category(Base):
    """카테고리 테이블"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 이 카테고리에 속한 상품 목록
    products = relationship("Product", back_populates="category")


class Product(Base):
    """상품 테이블 — 완제품/원자재 모두 이 테이블에 저장, category로 구분"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
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

    # 속한 카테고리 객체에 접근
    category = relationship("Category", back_populates="products")


class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 이 주문에 속한 항목 목록
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """주문 항목 테이블"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    # 주문 시점의 가격을 저장 — 나중에 상품 가격이 변해도 주문 내역은 유지되어야 하기 때문

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 42] Process 모델 (★★☆)                     │
# │                                                    │
# │ 공정(Process) 테이블 정의.                         │
# │ 자기참조 FK로 트리 구조를 구현합니다.              │
# │                                                    │
# │ 필드:                                              │
# │ - id, name(String(200), nullable=False)            │
# │ - description(Text, nullable=True)                 │
# │ - sequence_order(Integer, nullable=False)          │
# │   → 같은 부모 아래에서의 실행 순서                 │
# │ - parent_id(Integer, ForeignKey("processes.id"),   │
# │             nullable=True) → NULL = 최상위 공정    │
# │ - is_active(Boolean, default=True)                 │
# │ - created_at                                       │
# └──────────────────────────────────────────────────┘
class Process(Base):
    """공정 테이블 — 자기참조 FK로 공정 트리(부모-자식 계층) 표현"""
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)
    # 최상위 공정은 NULL, 하위 공정은 부모 공정의 id를 가짐
    parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 43] Process 자기참조 relationship (★★☆)    │
    # │                                                    │
    # │ - children: 이 공정의 하위 공정 목록               │
    # │ - parent: 이 공정의 상위 공정                      │
    # │                                                    │
    # │ remote_side=[id] 의미:                             │
    # │ "부모" 역할을 하는 쪽의 컬럼이 id임을 명시.        │
    # │ 즉, parent_id → processes.id 방향에서              │
    # │ id 쪽이 "one(부모)", parent_id 쪽이 "many(자식)"   │
    # └──────────────────────────────────────────────────┘
    children = relationship("Process", back_populates="parent")
    parent = relationship("Process", back_populates="children", remote_side=[id])


# ┌──────────────────────────────────────────────────┐
# │ [TODO 44] BOMEntry 모델 (★★☆)                    │
# │                                                    │
# │ 자재명세서(BOM) 항목 테이블.                       │
# │ Product 테이블을 완제품/자재 양쪽으로 참조합니다.  │
# │                                                    │
# │ 필드:                                              │
# │ - product_id → products.id (완제품)               │
# │ - material_id → products.id (자재)                │
# │ - quantity(Float) — 소수점 허용 (0.5kg 등)        │
# │ - unit(String(20), default="ea")                  │
# │                                                    │
# │ foreign_keys 명시가 필요한 이유:                   │
# │ 같은 테이블(products)을 두 FK로 참조하므로         │
# │ SQLAlchemy가 어느 FK를 쓸지 스스로 판단 불가.      │
# └──────────────────────────────────────────────────┘
class BOMEntry(Base):
    """자재명세서(BOM) 항목 — 완제품 한 개를 만들기 위한 자재 목록"""
    __tablename__ = "bom_entries"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="ea")

    # 동일 테이블을 두 번 참조하므로 foreign_keys로 각 relationship이 사용할 FK를 명시
    product = relationship("Product", foreign_keys=[product_id])
    material = relationship("Product", foreign_keys=[material_id])
