"""day6/practice/main.py"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day6.practice.database import engine, Base, get_db
from day6.practice import models  # noqa: F401
from day6.practice.routes import brands, items, departments, recipes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 6 (Practice)",
    description="Department(자기참조) + Recipe(Dual FK) 변형 문제",
    version="1.0.0",
)

app.include_router(brands.router)
app.include_router(items.router)
app.include_router(departments.router)
app.include_router(recipes.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
