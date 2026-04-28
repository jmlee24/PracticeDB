"""
day6/practice/models.py — Department(자기참조) + Recipe(dual FK) (TODO 빈칸)
================================================================
[과제]
   complete  →  practice
   ────────     ────────
   Process    →  Department  (자기참조 트리. 부서 조직도.)
   BOMEntry   →  Recipe       (dual FK to Item. 레시피 = 어느 Item 에 어느 Item 이 들어가는지.)

핵심 패턴은 동일:
   - Department.parent_id 로 자기참조 트리
   - Recipe 가 같은 items 테이블을 product_id, material_id 로 두 번 참조
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float,
    Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day6.practice.database import Base


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


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 1] Department 모델 (자기참조 FK)                      │
# │                                                            │
# │ __tablename__ = "departments"                              │
# │                                                            │
# │ 필드:                                                      │
# │ - id: Integer, PK, index=True                              │
# │ - name: String(200), NOT NULL                              │
# │ - description: Text, nullable=True                         │
# │ - parent_id: Integer, ForeignKey("departments.id"),        │
# │              nullable=True                                 │
# │ - created_at: DateTime, UTC 기본                           │
# │                                                            │
# │ relationship (complete 의 Process 패턴 그대로):            │
# │ - parent = relationship("Department",                      │
# │       remote_side="Department.id",                         │
# │       back_populates="children")                           │
# │ - children = relationship("Department",                    │
# │       back_populates="parent")                             │
# │                                                            │
# │ 함정: remote_side 누락 시 SQLAlchemy 가 자기참조 방향을    │
# │       못 정해 NoForeignKeysError 발생.                     │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 2] Recipe 모델 (Dual FK to Item)                      │
# │                                                            │
# │ __tablename__ = "recipes"                                  │
# │                                                            │
# │ 필드:                                                      │
# │ - id: Integer, PK, index=True                              │
# │ - product_id: Integer, ForeignKey("items.id"), NOT NULL    │
# │   (만들어지는 Item)                                        │
# │ - material_id: Integer, ForeignKey("items.id"), NOT NULL   │
# │   (필요한 Item — 같은 items 테이블 두 번째 참조)           │
# │ - quantity: Float, NOT NULL                                │
# │ - unit: String(20), NOT NULL, default="ea"                 │
# │                                                            │
# │ relationship 핵심 (foreign_keys 명시 필수!):               │
# │ - product = relationship("Item", foreign_keys=[product_id])│
# │ - material = relationship("Item",                          │
# │              foreign_keys=[material_id])                   │
# │                                                            │
# │ 함정: foreign_keys 빠뜨리면 AmbiguousForeignKeysError!     │
# │       complete 의 BOMEntry 라인을 그대로 패턴 적용.        │
# └──────────────────────────────────────────────────────────┘
