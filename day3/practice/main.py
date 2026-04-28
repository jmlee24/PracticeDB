"""day3/practice/main.py — FastAPI 앱"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day3.practice.database import engine, Base, get_db
from day3.practice import models  # noqa: F401
from day3.practice.routes import brands, items, bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 3 (Practice)",
    description="트랜잭션 실습 — Booking/BookingSeat 좌석 예약 변형 문제",
    version="1.0.0",
)

app.include_router(brands.router)
app.include_router(items.router)
app.include_router(bookings.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
