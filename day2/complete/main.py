"""
day2/complete/main.py — FastAPI 앱 (완성형)
================================================================
실행: uvicorn day2.complete.main:app --reload
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day2.complete.database import engine, Base, get_db
from day2.complete import models  # noqa: F401
from day2.complete.routes import categories, products

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 2 (Complete)",
    description="외래키(FK) + relationship — Category 1:N Product 완성 참고용",
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
