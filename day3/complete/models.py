"""
day3/complete/models.py — Day2 모델 + Order/OrderItem (완성형, 줄단위 해설)
================================================================
Day 3 의 핵심: 한 요청으로 여러 테이블 동시 변경 → 트랜잭션 원자성.

테이블 4개:
    categories (1) ─< products (N)             ← Day 2 와 동일
    orders     (1) ─< order_items (N) >─ products  ← Day 3 신규
    한 주문(Order)에 여러 항목(OrderItem). 각 항목은 어느 상품(Product)인지 가리킴.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day3.complete.database import Base


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
    category = relationship("Category", back_populates="products")


class Order(Base):
    """
    주문 테이블 — 트랜잭션의 부모 객체.

    status 는 단순 문자열로 저장 ("pending"/"cancelled"). Day 7 에서 본격 상태머신화.
    total_amount 는 INSERT 시점에 0 으로 시작 → items 처리 후 누적해 갱신.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_amount = Column(Integer, default=0)  # 합계 — 라우트에서 누적해 채움
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # nested 응답의 핵심. OrderItem 들이 자동으로 items 리스트로 직렬화된다.
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    주문 항목 테이블 — 한 주문의 자식.

    중요: unit_price 는 "주문 시점의 가격을 고정 저장" 한다.
          나중에 Product.price 가 바뀌어도 과거 주문 내역의 단가는 그대로 유지되어야 함.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)  # 주문 시점 가격 스냅샷

    order = relationship("Order", back_populates="items")
    product = relationship("Product")  # 단방향. Product 쪽엔 back_populates 없음.
