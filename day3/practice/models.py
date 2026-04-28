"""
day3/practice/models.py — Day2 practice 모델 + Booking/BookingSeat (TODO 빈칸)
================================================================
[과제] complete 의 Order/OrderItem 트랜잭션을 Booking/BookingSeat 좌석 예약으로 변형.

매핑:
    complete                practice
    --------                --------
    Order              →    Booking      (예약)
    OrderItem          →    BookingSeat  (예약 좌석)
    customer_name      →    customer_name (동일)
    total_amount       →    total_price
    quantity (수량)     →    seat_count   (좌석 수)
    unit_price (단가)   →    seat_price
    Product.stock 차감  →    Item.stock 차감 (의미: '잔여 좌석')
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day3.practice.database import Base


# Brand / Item — Day 2 practice 와 동일 (참고용 완성)
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
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)   # ← 좌석 잔여수로 사용
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    brand = relationship("Brand", back_populates="items")


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 1] Booking 모델                                       │
# │                                                            │
# │ __tablename__ = "bookings"                                 │
# │                                                            │
# │ 필드:                                                      │
# │ - id: Integer, PK, index=True                              │
# │ - customer_name: String(200), nullable=False               │
# │ - status: String(20), nullable=False, default="pending"    │
# │ - total_price: Integer, default=0                          │
# │ - created_at: DateTime, UTC 기본값 (Day1 패턴)             │
# │                                                            │
# │ relationship:                                              │
# │ - seats: relationship("BookingSeat", back_populates="booking") │
# │                                                            │
# │ 힌트: complete 의 Order 클래스 통째로 보고                  │
# │       items → seats, total_amount → total_price 만 변경    │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 2] BookingSeat 모델                                   │
# │                                                            │
# │ __tablename__ = "booking_seats"                            │
# │                                                            │
# │ 필드:                                                      │
# │ - id: Integer, PK, index=True                              │
# │ - booking_id: Integer, ForeignKey("bookings.id"), NOT NULL │
# │ - item_id: Integer, ForeignKey("items.id"), NOT NULL       │
# │ - seat_count: Integer, NOT NULL                            │
# │ - seat_price: Integer, NOT NULL  ← 예약 시점 좌석 단가 고정 │
# │                                                            │
# │ relationship:                                              │
# │ - booking: relationship("Booking", back_populates="seats") │
# │ - item: relationship("Item")  (단방향)                     │
# │                                                            │
# │ 힌트: complete 의 OrderItem 클래스 패턴 참고               │
# └──────────────────────────────────────────────────────────┘
