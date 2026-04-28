"""
day2/practice/main.py — FastAPI 앱 (그대로 사용)
================================================================
실행: uvicorn day2.practice.main:app --reload --port 8001
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day2.practice.database import engine, Base, get_db
from day2.practice import models  # noqa: F401
from day2.practice.routes import brands, items

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 2 (Practice)",
    description="외래키 + relationship 실습 — Brand 1:N Item 변형 문제",
    version="1.0.0",
)

app.include_router(brands.router)
app.include_router(items.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
