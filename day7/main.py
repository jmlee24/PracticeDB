"""
FastAPI 앱 진입점
================
실행: uvicorn day7.main:app --reload
Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI

from day7.database import engine, Base
from day7.routes import categories, products, orders, processes, bom, work_orders

# 앱 시작 시 모든 테이블 자동 생성 (이미 존재하면 무시)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 7",
    description="MES 작업지시 + 상태머신 — WorkOrder/WorkOrderItem + 상태 전이 패턴",
    version="0.7.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(processes.router)
app.include_router(bom.router)
app.include_router(work_orders.router)


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
