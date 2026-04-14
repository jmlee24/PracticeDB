"""
SQLAlchemy 모델 (DB 테이블 정의)
================================
Day 2의 Category + Product 위에 Order, OrderItem을 추가합니다.

핵심 개념:
- ForeignKey: 다른 테이블의 컬럼을 참조해 테이블 간 관계를 만듦
- relationship: ORM 수준에서 관련 객체를 파이썬 속성처럼 접근 가능하게 함
- back_populates: 양방향 relationship 설정 시 서로를 연결하는 속성 이름
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day3.database import Base


class Category(Base):
    """카테고리 테이블 — Day 2 완성본"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 이 카테고리에 속한 상품 목록
    products = relationship("Product", back_populates="category")


class Product(Base):
    """상품 테이블 — Day 2 완성본"""
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


# ┌──────────────────────────────────────────────────┐
# │ [TODO 17] Order 모델 (★★☆)                        │
# │                                                    │
# │ __tablename__ = "orders"                           │
# │                                                    │
# │ 필드:                                              │
# │ - id: Integer, PK                                  │
# │ - customer_name: String(200), nullable=False       │
# │ - status: String(20), nullable=False,              │
# │           default="pending"                        │
# │ - total_amount: Integer, default=0                 │
# │ - created_at: DateTime, UTC 기본값                 │
# │                                                    │
# │ relationship:                                      │
# │ - items → OrderItem과 연결 (back_populates="order")│
# └──────────────────────────────────────────────────┘
class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # TODO 19에서 완성되는 relationship (미리 배치)
    items = relationship("OrderItem", back_populates="order")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 18] OrderItem 모델 (★★☆)                    │
# │                                                    │
# │ __tablename__ = "order_items"                      │
# │                                                    │
# │ 필드:                                              │
# │ - id: Integer, PK                                  │
# │ - order_id: Integer, ForeignKey("orders.id"),      │
# │             nullable=False                         │
# │ - product_id: Integer, ForeignKey("products.id"),  │
# │               nullable=False                       │
# │ - quantity: Integer, nullable=False                │
# │ - unit_price: Integer, nullable=False              │
# │   (주문 시점의 가격을 저장 — 나중에 상품 가격이    │
# │    변해도 주문 내역은 유지되어야 하기 때문)         │
# └──────────────────────────────────────────────────┘
class OrderItem(Base):
    """주문 항목 테이블"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 19] Order-OrderItem relationship (★☆☆)     │
    # │                                                    │
    # │ OrderItem 측 relationship 2개를 완성하세요.        │
    # │                                                    │
    # │ 1) order: Order와 연결                             │
    # │    - back_populates="items"                        │
    # │    - (Order.items ↔ OrderItem.order 양방향)        │
    # │                                                    │
    # │ 2) product: Product와 연결                         │
    # │    - 단방향이므로 back_populates 불필요             │
    # │                                                    │
    # │ 힌트:                                              │
    # │   order = relationship("Order",                    │
    # │       back_populates="items")                      │
    # │   product = relationship("Product")               │
    # └──────────────────────────────────────────────────┘
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
