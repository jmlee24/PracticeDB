"""
SQLAlchemy 모델 (DB 테이블 정의)
================================
Day 6 완성본 — Category, Product, Order, OrderItem, Process, BOMEntry 완성.
Day 7 추가 — WorkOrder(작업지시), WorkOrderItem(소요자재) + 상태 전이 패턴.

핵심 개념:
- 자기참조 FK: Process가 자신의 부모 공정을 참조
- Dual FK: BOMEntry가 같은 products 테이블을 두 개의 FK로 참조
- 상태 머신: WorkOrder의 status는 ALLOWED_TRANSITIONS 딕셔너리로 전이 규칙을 관리
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day7.database import Base


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
    """상품 테이블 — 완제품과 원자재 모두 이 테이블에 저장"""
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

    # 속한 카테고리 객체에 접근
    category = relationship("Category", back_populates="products")

    # BOM에서 이 제품이 완제품으로 등록된 항목들
    bom_as_product = relationship(
        "BOMEntry",
        foreign_keys="BOMEntry.product_id",
        back_populates="product",
    )

    # BOM에서 이 제품이 자재로 등록된 항목들
    bom_as_material = relationship(
        "BOMEntry",
        foreign_keys="BOMEntry.material_id",
        back_populates="material",
    )


class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
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


class Process(Base):
    """
    공정 테이블
    ──────────
    제조 과정에서 수행되는 작업 단계를 정의합니다.
    parent_id로 자기참조 FK를 사용해 공정 계층(트리)을 표현합니다.
    예: 조립 공정 > 부품 조립 > 나사 조임
    """
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # 자기참조 FK — 상위 공정이 없는 루트 공정은 NULL
    # nullable=True: 최상위 공정은 부모가 없음
    parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 자기참조 relationship — 같은 클래스를 문자열로 지정
    # remote_side: 부모 쪽 컬럼을 명시해 방향을 결정
    parent = relationship("Process", remote_side="Process.id", back_populates="children")
    children = relationship("Process", back_populates="parent")


class BOMEntry(Base):
    """
    BOM(Bill of Materials, 자재명세서) 테이블
    ─────────────────────────────────────────
    완제품 1개를 만들 때 필요한 자재 목록을 정의합니다.
    product_id: 만들어지는 완제품
    material_id: 필요한 자재 (원자재 또는 반제품)

    Dual FK 패턴: 같은 products 테이블을 두 개의 FK로 참조.
    relationship에서 foreign_keys를 명시해 SQLAlchemy가 혼동하지 않도록 해야 함.
    """
    __tablename__ = "bom_entries"

    id = Column(Integer, primary_key=True, index=True)

    # 만들어지는 완제품 — products 테이블의 id를 참조
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # 필요한 자재 — 같은 products 테이블을 참조 (Dual FK)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # BOM 기준 필요 수량 (소수점 허용: 0.5kg, 2.5L 등)
    quantity = Column(Float, nullable=False)

    # foreign_keys로 어느 FK를 사용하는 relationship인지 명시
    product = relationship(
        "Product",
        foreign_keys=[product_id],
        back_populates="bom_as_product",
    )
    material = relationship(
        "Product",
        foreign_keys=[material_id],
        back_populates="bom_as_material",
    )


# ┌──────────────────────────────────────────────────┐
# │ [TODO 54] WorkOrder 모델 (★★☆)                    │
# │                                                    │
# │ __tablename__ = "work_orders"                      │
# │                                                    │
# │ 필드:                                              │
# │ - id: Integer, PK                                  │
# │ - order_number: String(50), unique=True,           │
# │                 nullable=False                     │
# │ - product_id: Integer,                             │
# │               ForeignKey("products.id"),           │
# │               nullable=False — 만들 완제품          │
# │ - process_id: Integer,                             │
# │               ForeignKey("processes.id"),          │
# │               nullable=False — 어떤 공정으로        │
# │ - quantity: Integer, nullable=False — 생산 수량     │
# │ - status: String(20), nullable=False,              │
# │           default="PENDING"                        │
# │ - created_at: DateTime, UTC 기본값                 │
# │ - started_at: DateTime, nullable=True              │
# │ - completed_at: DateTime, nullable=True            │
# └──────────────────────────────────────────────────┘
class WorkOrder(Base):
    """작업지시 테이블 — 어떤 완제품을 몇 개, 어떤 공정으로 만들지 정의"""
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)

    # 작업지시 번호 — 서버에서 자동 생성 (예: WO-20240101120000)
    order_number = Column(String(50), unique=True, nullable=False)

    # 만들어야 할 완제품 ID
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # 사용할 공정 ID
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)

    # 생산 목표 수량
    quantity = Column(Integer, nullable=False)

    # 상태: PENDING → IN_PROGRESS → COMPLETED / CANCELLED
    status = Column(String(20), nullable=False, default="PENDING", index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 작업 시작/완료 시각 — 아직 시작/완료 전이면 NULL
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 56] WorkOrder relationships (★☆☆)          │
    # │                                                    │
    # │ - product: 만들 완제품 (Product)                  │
    # │ - process: 사용할 공정 (Process)                  │
    # │ - items: 소요 자재 목록 (WorkOrderItem list)       │
    # └──────────────────────────────────────────────────┘
    product = relationship("Product", foreign_keys=[product_id])
    process = relationship("Process")
    items = relationship("WorkOrderItem", back_populates="work_order")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 55] WorkOrderItem 모델 (★★☆)                │
# │                                                    │
# │ __tablename__ = "work_order_items"                 │
# │                                                    │
# │ 필드:                                              │
# │ - id: Integer, PK                                  │
# │ - work_order_id: Integer,                          │
# │                  ForeignKey("work_orders.id"),     │
# │                  nullable=False                    │
# │ - material_id: Integer,                            │
# │                ForeignKey("products.id"),          │
# │                nullable=False                      │
# │ - required_qty: Float, nullable=False              │
# │                 — BOM 기준 필요량                   │
# │ - consumed_qty: Float, nullable=False, default=0   │
# │                 — 실제 소비량                       │
# └──────────────────────────────────────────────────┘
class WorkOrderItem(Base):
    """작업지시 소요자재 테이블 — 작업지시 1건당 필요한 자재 목록"""
    __tablename__ = "work_order_items"

    id = Column(Integer, primary_key=True, index=True)

    # 소속 작업지시 ID
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # 필요한 자재 — products 테이블 참조 (원자재/반제품)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # BOM에서 계산된 필요량 (생산수량 × BOM 단위수량)
    required_qty = Column(Float, nullable=False)

    # 실제로 투입된 수량 — 작업 진행 중 실적 등록 시 갱신
    consumed_qty = Column(Float, nullable=False, default=0)

    # TODO 56 — WorkOrderItem relationships
    work_order = relationship("WorkOrder", back_populates="items")
    material = relationship("Product", foreign_keys=[material_id])
