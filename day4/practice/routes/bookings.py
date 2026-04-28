"""
day4/practice/routes/bookings.py — Booking 페이지네이션 (TODO 일부)
================================================================
Day 3 practice 의 Booking 트랜잭션 + Day 4 페이지네이션 결합.
create/get 은 완성. list 만 페이지네이션 + status 필터 TODO.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.practice.database import get_db
from day4.practice.models import Booking, BookingSeat, Item
from day4.practice.schemas import BookingCreate, BookingResponse, PaginatedResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    """완성. Day 3 practice 의 트랜잭션 패턴 그대로."""
    try:
        booking = Booking(customer_name=data.customer_name)
        db.add(booking); db.flush()
        total = 0
        for s in data.seats:
            item = db.query(Item).filter(Item.id == s.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail=f"상품 ID {s.item_id} 없음")
            if item.stock < s.seat_count:
                raise HTTPException(status_code=400, detail=f"'{item.name}' 좌석 부족")
            item.stock -= s.seat_count
            db.add(BookingSeat(
                booking_id=booking.id, item_id=s.item_id,
                seat_count=s.seat_count, seat_price=item.price,
            ))
            total += item.price * s.seat_count
        booking.total_price = total
        db.commit(); db.refresh(booking)
        return booking
    except HTTPException:
        db.rollback(); raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="예약 처리 중 오류")


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 2] 예약 목록 페이지네이션 + status 필터               │
# │                                                            │
# │ Query: page, size, status (str | None)                     │
# │                                                            │
# │ 본문(complete orders.py list_orders 패턴):                 │
# │   query = db.query(Booking)                                │
# │   if status: query = query.filter(Booking.status == status)│
# │   total = query.count()                                    │
# │   items = query.offset((page-1)*size).limit(size).all()    │
# │   return PaginatedResponse(...)                            │
# └──────────────────────────────────────────────────────────┘


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """완성."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")
    return booking
