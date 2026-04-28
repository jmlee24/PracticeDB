"""
day5/practice/models.py — Day4 practice + 인덱스 + barcode 컬럼 (TODO 빈칸)
================================================================
[과제] complete 의 인덱스/유니크 제약 패턴을 Item 에 적용.

매핑:
    complete                    practice
    --------                    --------
    Product.name index=True →  Item.name index=True
    Order.status index=True →  Booking.status index=True
    Index(customer_name,        Index(customer_name,
       created_at)                 created_at) on Booking
    UQ(name, category_id)   →  UQ(name, brand_id) on Item
    (없음)                  →  Item.barcode 컬럼 추가 + unique 인덱스 (신규!)
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey,
    Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day5.practice.database import Base


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

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 1] Item.name 에 index=True 추가                  │
    # │                                                        │
    # │ 변경 전: name = Column(String(200), nullable=False)    │
    # │ 변경 후: name = Column(String(200), nullable=False,    │
    # │                       index=True)                      │
    # │                                                        │
    # │ 힌트: complete 의 Product.name 라인 참고               │
    # └──────────────────────────────────────────────────────┘
    name = Column(String(200), nullable=False)

    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 2] barcode 컬럼 추가 (신규!)                     │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 타입: String(50)                                     │
    # │ - NULL 허용 (기존 데이터 호환)                         │
    # │ - 단일 unique 인덱스 (한 상품에만 한 바코드)           │
    # │                                                        │
    # │ 힌트: barcode = Column(String(50), nullable=True,      │
    # │                        unique=True, index=True)        │
    # │                                                        │
    # │ 또는 unique=True 만 줘도 PostgreSQL 이 자동 인덱스 생성│
    # └──────────────────────────────────────────────────────┘

    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    brand = relationship("Brand", back_populates="items")

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 3] __table_args__ 추가                            │
    # │                                                        │
    # │ 복합 유니크: 같은 brand 안에서 이름 중복 금지          │
    # │   (다른 brand 에는 같은 이름 허용)                     │
    # │                                                        │
    # │ 힌트(complete 의 Product 패턴):                        │
    # │   __table_args__ = (                                   │
    # │       UniqueConstraint("name", "brand_id",             │
    # │                        name="uq_item_name_brand"),     │
    # │   )                                                    │
    # │                                                        │
    # │ 함정: 항목 1개여도 끝에 콤마(,) 필수!                  │
    # └──────────────────────────────────────────────────────┘


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 4] Booking.status 에 index=True 추가             │
    # │                                                        │
    # │ 힌트(complete 의 Order.status 와 동일 패턴):           │
    # │   status = Column(String(20), nullable=False,          │
    # │                   default="pending", index=True)       │
    # └──────────────────────────────────────────────────────┘
    status = Column(String(20), nullable=False, default="pending")

    total_price = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    seats = relationship("BookingSeat", back_populates="booking")

    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 5] 복합 인덱스 추가                               │
    # │                                                        │
    # │ Index 이름: ix_bookings_customer_created               │
    # │ 컬럼: customer_name, created_at                        │
    # │                                                        │
    # │ 힌트(complete 의 Order 패턴):                          │
    # │   __table_args__ = (                                   │
    # │       Index("ix_bookings_customer_created",            │
    # │             "customer_name", "created_at"),            │
    # │   )                                                    │
    # └──────────────────────────────────────────────────────┘


class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    seat_count = Column(Integer, nullable=False)
    seat_price = Column(Integer, nullable=False)
    booking = relationship("Booking", back_populates="seats")
    item = relationship("Item")
