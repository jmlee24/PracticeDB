"""
day7/practice/models.py — Day6 practice + Shipment 상태머신 (TODO 빈칸)
================================================================
[과제]
   complete (작업지시)        practice (출고지시)
   ──────────                  ──────────
   WorkOrder                  Shipment
   WorkOrderItem              ShipmentItem
   상태: PENDING/IN_PROGRESS/  상태: PENDING/SHIPPING/
        COMPLETED/CANCELED         DELIVERED/RETURNED + HOLD (신규!)

요지: HOLD 상태가 추가되어 PENDING ↔ HOLD 양방향 전이 가능.
      complete 의 모델 구조는 그대로 옮기고, 라우트 ALLOWED_TRANSITIONS 만 확장.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day7.practice.database import Base


# Brand / Item — Day 6 practice 와 동일 (참고용 완성)
class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    items = relationship("Item", back_populates="brand")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    brand = relationship("Brand", back_populates="items")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    parent = relationship("Department", remote_side="Department.id", back_populates="children")
    children = relationship("Department", back_populates="parent")


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="ea")
    product = relationship("Item", foreign_keys=[product_id])
    material = relationship("Item", foreign_keys=[material_id])


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 1] Shipment 모델                                      │
# │                                                            │
# │ __tablename__ = "shipments"                                │
# │                                                            │
# │ 필드:                                                      │
# │ - id: Integer, PK, index=True                              │
# │ - shipment_number: String(50), unique=True, NOT NULL       │
# │ - product_id: Integer, ForeignKey("items.id"), NOT NULL    │
# │ - department_id: Integer,                                  │
# │     ForeignKey("departments.id"), NOT NULL                 │
# │ - quantity: Integer, NOT NULL                              │
# │ - status: String(20), NOT NULL, default="PENDING",         │
# │           index=True                                       │
# │ - created_at: DateTime, UTC 기본                           │
# │ - shipped_at: DateTime, nullable=True                      │
# │ - delivered_at: DateTime, nullable=True                    │
# │                                                            │
# │ relationship:                                              │
# │ - product = relationship("Item",                           │
# │     foreign_keys=[product_id])                             │
# │ - department = relationship("Department")                  │
# │ - items = relationship("ShipmentItem",                     │
# │     back_populates="shipment")                             │
# │                                                            │
# │ 힌트: complete 의 WorkOrder 와 같은 구조.                   │
# │       order_number → shipment_number,                      │
# │       process_id → department_id,                          │
# │       started_at → shipped_at,                             │
# │       completed_at → delivered_at                          │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 2] ShipmentItem 모델                                  │
# │                                                            │
# │ __tablename__ = "shipment_items"                           │
# │                                                            │
# │ 필드:                                                      │
# │ - id: Integer, PK, index=True                              │
# │ - shipment_id: Integer,                                    │
# │     ForeignKey("shipments.id"), NOT NULL                   │
# │ - material_id: Integer,                                    │
# │     ForeignKey("items.id"), NOT NULL                       │
# │ - required_qty: Float, NOT NULL                            │
# │ - actual_qty: Float, NOT NULL, default=0                   │
# │                                                            │
# │ relationship:                                              │
# │ - shipment = relationship("Shipment",                      │
# │     back_populates="items")                                │
# │ - material = relationship("Item",                          │
# │     foreign_keys=[material_id])                            │
# │                                                            │
# │ 힌트: complete 의 WorkOrderItem 패턴.                       │
# │       consumed_qty → actual_qty                            │
# └──────────────────────────────────────────────────────────┘
