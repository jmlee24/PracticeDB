"""day7/complete/main.py"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day7.complete.database import engine, Base, get_db
from day7.complete import models  # noqa: F401
from day7.complete.routes import categories, products, processes, bom, work_orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 7 (Complete)",
    description="MES — WorkOrder 상태머신 + BOM 자재 차감 트랜잭션 완성 참고용",
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(processes.router)
app.include_router(bom.router)
app.include_router(work_orders.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
