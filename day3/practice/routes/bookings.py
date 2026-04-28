"""
day3/practice/routes/bookings.py — Booking 트랜잭션 (TODO 빈칸)
================================================================
[과제] complete/routes/orders.py 의 트랜잭션 패턴을 Booking 으로 옮긴다.

핵심 차이:
    - 의미: 재고 차감 → 좌석 차감 (Item.stock 을 좌석 잔여수로 해석)
    - 필드: quantity → seat_count, unit_price → seat_price, total_amount → total_price

참고: complete 의 create_order 함수 전체.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day3.practice.database import get_db
# from day3.practice.models import Booking, BookingSeat, Item       # ← TODO 1, 2 완성 시 활성
# from day3.practice.schemas import BookingCreate, BookingResponse  # ← TODO 4, 6 완성 시 활성

router = APIRouter(prefix="/bookings", tags=["bookings"])


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 7] 예약 생성 (POST /bookings/)                       │
# │                                                            │
# │ 핵심 트랜잭션 패턴 (complete create_order 와 동일):         │
# │   try:                                                     │
# │     booking = Booking(customer_name=...)                   │
# │     db.add(booking)                                        │
# │     db.flush()                       # ← booking.id 확보   │
# │     total = 0                                              │
# │     for s in data.seats:                                   │
# │       item = db.query(Item).filter(Item.id == s.item_id)\  │
# │                .first()                                    │
# │       if not item: raise HTTPException(404, ...)           │
# │       if item.stock < s.seat_count:                        │
# │           raise HTTPException(400, "좌석 부족")            │
# │       item.stock -= s.seat_count                           │
# │       db.add(BookingSeat(                                  │
# │           booking_id=booking.id, item_id=s.item_id,        │
# │           seat_count=s.seat_count, seat_price=item.price)) │
# │       total += item.price * s.seat_count                   │
# │     booking.total_price = total                            │
# │     db.commit(); db.refresh(booking); return booking       │
# │   except HTTPException: db.rollback(); raise               │
# │   except Exception: db.rollback(); raise HTTPException(500)│
# │                                                            │
# │ 함정: rollback 누락 시 세션 오염 → 이후 모든 요청 실패!    │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 8] 예약 목록 (GET /bookings/)                        │
# │                                                            │
# │ 힌트(complete list_orders 와 동일):                        │
# │   return db.query(Booking).all()                           │
# │                                                            │
# │ from_attributes=True 덕분에 seats 배열이 자동 직렬화됨.    │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 9] 예약 단건 조회 (GET /bookings/{booking_id})       │
# │                                                            │
# │ 힌트: complete get_order 와 완전 동일                      │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 10] 예약 취소 (DELETE /bookings/{booking_id}/cancel) │
# │                                                            │
# │ - status == "cancelled" → 400 (이중 취소 방지)             │
# │ - status = "cancelled" 로 변경                             │
# │ - 각 seat 에 대해 Item.stock += seat_count (좌석 원복)     │
# │ - try/except + db.rollback                                 │
# │                                                            │
# │ 힌트: complete cancel_order 패턴 그대로                    │
# └──────────────────────────────────────────────────────────┘
