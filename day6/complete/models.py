"""
day6/complete/models.py — Day5 + Process(자기참조) + BOMEntry(dual FK) (완성형)
================================================================
Day 6 의 두 핵심 패턴:

1) 자기참조 FK (Process.parent_id → processes.id)
   같은 테이블의 다른 행을 가리킴. 트리 구조 표현.

2) 같은 테이블 두 번 참조 (BOMEntry.product_id, material_id → products.id)
   relationship 마다 foreign_keys=[col] 명시 필수.
   안 그러면 'AmbiguousForeignKeysError' 발생.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float,
    Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day6.complete.database import Base


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
    """
    공정 테이블 — 트리 구조 (자기참조 FK).

    예:
        SMT 실장 (id=1, parent_id=NULL)            ← 최상위
          ├─ 부품 배치 (id=2, parent_id=1)
          └─ 납땜     (id=3, parent_id=1)
        검사    (id=4, parent_id=NULL)             ← 최상위

    DB 레벨: parent_id 가 같은 테이블의 id 를 참조.
    """
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # 자기참조 FK — "processes.id" 라고 자기 자신 테이블을 가리킴.
    # nullable=True 이므로 최상위 공정은 parent_id=NULL.
    parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 자기참조 relationship 두 개 — children/parent 양방향.
    #
    # 'parent' 정의의 핵심:
    #   remote_side="Process.id" 로 "어느 컬럼이 부모(one) 쪽인지" 명시.
    #   자기참조에서는 두 쪽 모두 같은 테이블이라 SQLAlchemy 가 방향을 못 정함.
    #   id 컬럼이 부모 = parent_id 컬럼이 자식.
    parent = relationship(
        "Process",
        remote_side="Process.id",
        back_populates="children",
    )
    children = relationship("Process", back_populates="parent")


class BOMEntry(Base):
    """
    BOM(Bill of Materials, 자재명세서) 항목.

    완제품 1개를 만드는 데 필요한 자재 목록.
    완제품도 자재도 모두 products 테이블에 저장 (category 로 구분).

    Dual FK 패턴:
        product_id   → products.id  (완제품)
        material_id  → products.id  (자재)
        둘 다 같은 테이블을 가리킴 → relationship 에 foreign_keys=[col] 명시 필수.
    """
    __tablename__ = "bom_entries"

    id = Column(Integer, primary_key=True, index=True)

    # FK 1: 완제품
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # FK 2: 자재 (같은 products 테이블)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # quantity 는 Float — 0.5kg, 2.5L 등 소수점 허용.
    quantity = Column(Float, nullable=False)

    # 단위: "ea"(개수), "kg", "L" 등
    unit = Column(String(20), nullable=False, default="ea")

    # foreign_keys=[col] 가 핵심.
    # 어느 FK 를 통해 이 relationship 이 연결되는지 명시.
    # 빠뜨리면: sqlalchemy.exc.AmbiguousForeignKeysError 즉시 발생.
    product = relationship("Product", foreign_keys=[product_id])
    material = relationship("Product", foreign_keys=[material_id])
