"""day3/complete/main.py — FastAPI 앱"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day3.complete.database import engine, Base, get_db
from day3.complete import models  # noqa: F401
from day3.complete.routes import categories, products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 3 (Complete)",
    description="트랜잭션 + nested 응답 — 주문 시스템 완성 참고용",
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
