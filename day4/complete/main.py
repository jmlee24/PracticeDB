"""day4/complete/main.py — FastAPI 앱"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day4.complete.database import engine, Base, get_db
from day4.complete import models  # noqa: F401
from day4.complete.routes import categories, products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 4 (Complete)",
    description="페이지네이션 + 검색 + 동적 정렬 — 통합 목록 API 완성 참고용",
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
