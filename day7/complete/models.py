"""
day7/complete/models.py — Day6 + WorkOrder/WorkOrderItem (완성형)
================================================================
Day 7 핵심:
    - 상태 머신 status 필드
    - BOM 기반 자재 소요량 계산
    - 시작/완료/취소 시 자재 차감/원복 트랜잭션
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day7.complete.database import Base


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


class Process(Base):
    __tablename__ = "processes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    parent = relationship("Process", remote_side="Process.id", back_populates="children")
    children = relationship("Process", back_populates="parent")


class BOMEntry(Base):
    __tablename__ = "bom_entries"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="ea")
    product = relationship("Product", foreign_keys=[product_id])
    material = relationship("Product", foreign_keys=[material_id])


class WorkOrder(Base):
    """
    작업지시 — 어떤 완제품을 몇 개 만들지 지시.

    상태 머신 전이도:

        ┌─────────┐  start    ┌──────────────┐  complete  ┌───────────┐
        │ PENDING │ ────────▶ │ IN_PROGRESS  │ ─────────▶ │ COMPLETED │
        └────┬────┘           └──┬───────────┘            └───────────┘
             │ cancel             │ cancel
             ▼                    ▼
        ┌──────────┐         ┌──────────┐
        │ CANCELED │         │ CANCELED │
        └──────────┘         └──────────┘

    routes/work_orders.py 의 ALLOWED_TRANSITIONS dict 가 이 그림을 코드로 표현.
    """
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)

    # 서버가 자동 생성: WO-YYYYMMDDHHMMSS 형식. unique 로 충돌 방지.
    order_number = Column(String(50), unique=True, nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    # 상태 — 4가지 ENUM 값. index 로 status 별 조회 빠르게.
    status = Column(String(20), nullable=False, default="PENDING", index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)     # 시작 전엔 NULL
    completed_at = Column(DateTime, nullable=True)   # 완료 전엔 NULL

    product = relationship("Product", foreign_keys=[product_id])
    process = relationship("Process")
    items = relationship("WorkOrderItem", back_populates="work_order")


class WorkOrderItem(Base):
    """
    작업지시 소요자재 — BOM 기반으로 작업지시 생성 시 자동 채워짐.

    required_qty = BOMEntry.quantity × WorkOrder.quantity
    consumed_qty = 실제 작업하면서 투입한 양 (실적 등록 시 갱신)

    Float 인 이유: 0.5kg, 2.5L 등 소수점 자재 허용.
    """
    __tablename__ = "work_order_items"
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    required_qty = Column(Float, nullable=False)
    consumed_qty = Column(Float, nullable=False, default=0)
    work_order = relationship("WorkOrder", back_populates="items")
    material = relationship("Product", foreign_keys=[material_id])
