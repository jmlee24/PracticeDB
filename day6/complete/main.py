"""day6/complete/main.py"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day6.complete.database import engine, Base, get_db
from day6.complete import models  # noqa: F401
from day6.complete.routes import categories, products, processes, bom

# Day6 부터는 Alembic 사용 권장이지만, 학습 단순성을 위해 다시 create_all.
# 실제 운영 코드라면 Day5 처럼 Alembic 으로 관리.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 6 (Complete)",
    description="MES — 자기참조 공정 + BOM(Dual FK) 완성 참고용",
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(processes.router)
app.include_router(bom.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
