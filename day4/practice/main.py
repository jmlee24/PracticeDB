"""day4/practice/main.py — FastAPI 앱"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day4.practice.database import engine, Base, get_db
from day4.practice import models  # noqa: F401
from day4.practice.routes import brands, items, bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 4 (Practice)",
    description="페이지네이션 실습 — list_items 에 재고 범위 필터 적용",
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
