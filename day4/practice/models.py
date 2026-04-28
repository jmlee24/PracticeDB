"""day4/practice/models.py — Day3 practice 와 동일 (Brand/Item/Booking/BookingSeat)"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day4.practice.database import Base


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
    stock = Column(Integer, nullable=False, default=0)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    brand = relationship("Brand", back_populates="items")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_price = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    seats = relationship("BookingSeat", back_populates="booking")


class BookingSeat(Base):
    __tablename__ = "booking_seats"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    seat_count = Column(Integer, nullable=False)
    seat_price = Column(Integer, nullable=False)
    booking = relationship("Booking", back_populates="seats")
    item = relationship("Item")
