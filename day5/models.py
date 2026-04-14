"""
SQLAlchemy 모델 (DB 테이블 정의)
================================
Day 4 완성본 — Category, Product, Order, OrderItem 모두 완성.

Day 5 추가 학습: 인덱스와 제약 조건 추가
- index=True: 단일 컬럼 인덱스 (B-Tree, 조회 속도 O(log n))
- __table_args__: 복합 인덱스 / 복합 유니크 제약 조건

핵심 개념:
- ForeignKey: 다른 테이블의 컬럼을 참조해 테이블 간 관계를 만듦
- relationship: ORM 수준에서 관련 객체를 파이썬 속성처럼 접근 가능하게 함
- back_populates: 양방향 relationship 설정 시 서로를 연결하는 속성 이름
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day5.database import Base


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
    """상품 테이블"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 35] Product.name 단일 인덱스 추가 (★☆☆)    │
    # │                                                    │
    # │ 상품명으로 검색하는 쿼리가 많을 때 인덱스를        │
    # │ 추가하면 O(n) → O(log n)으로 성능이 향상됩니다.   │
    # │                                                    │
    # │ 현재 코드:                                         │
    # │   name = Column(String(200), nullable=False)       │
    # │                                                    │
    # │ 변경 후:                                           │
    # │   name = Column(String(200), nullable=False,       │
    # │                 index=True)                        │
    # └──────────────────────────────────────────────────┘
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

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 38] Product 복합 유니크 제약 추가 (★★☆)     │
    # │                                                    │
    # │ 같은 카테고리 내에서 상품명이 중복되지 않도록       │
    # │ 복합 유니크 제약을 추가합니다.                      │
    # │                                                    │
    # │ 추가할 코드:                                        │
    # │   from sqlalchemy import UniqueConstraint          │
    # │                                                    │
    # │   __table_args__ = (                               │
    # │       UniqueConstraint(                            │
    # │           "name", "category_id",                  │
    # │           name="uq_product_name_category",         │
    # │       ),                                           │
    # │   )                                                │
    # │                                                    │
    # │ 힌트: __table_args__는 클래스 바디 맨 아래,         │
    # │ relationship 선언 바로 위에 추가하세요.             │
    # └──────────────────────────────────────────────────┘

    # 속한 카테고리 객체에 접근
    category = relationship("Category", back_populates="products")


class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 36] Order.status 단일 인덱스 추가 (★☆☆)    │
    # │                                                    │
    # │ 주문 상태(pending/confirmed/cancelled)로           │
    # │ 필터링하는 쿼리가 많을 때 인덱스가 유용합니다.     │
    # │                                                    │
    # │ 현재 코드:                                         │
    # │   status = Column(String(20), nullable=False,      │
    # │                   default="pending")               │
    # │                                                    │
    # │ 변경 후:                                           │
    # │   status = Column(String(20), nullable=False,      │
    # │                   default="pending", index=True)   │
    # └──────────────────────────────────────────────────┘
    status = Column(String(20), nullable=False, default="pending")

    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 37] Order 복합 인덱스 추가 (★★☆)            │
    # │                                                    │
    # │ 고객명 + 생성일 기준으로 주문을 조회하는           │
    # │ 쿼리를 최적화하는 복합 인덱스를 추가합니다.        │
    # │                                                    │
    # │ 추가할 코드:                                        │
    # │   from sqlalchemy import Index                     │
    # │                                                    │
    # │   __table_args__ = (                               │
    # │       Index(                                       │
    # │           "ix_orders_customer_created",            │
    # │           "customer_name", "created_at",           │
    # │       ),                                           │
    # │   )                                                │
    # │                                                    │
    # │ 힌트: __table_args__는 클래스 바디 맨 아래,         │
    # │ relationship 선언 바로 위에 추가하세요.             │
    # └──────────────────────────────────────────────────┘

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
