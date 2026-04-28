"""day5/practice/main.py — Alembic 시대, create_all 제거됨"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day5.practice.database import get_db
from day5.practice import models  # noqa: F401
from day5.practice.routes import brands, items, bookings

# create_all 사용 안 함 — Alembic 이 테이블 관리

app = FastAPI(
    title="StudyDB Day 5 (Practice)",
    description="Alembic + 인덱스 실습 — barcode 추가 + Item UQ(name, brand_id)",
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
