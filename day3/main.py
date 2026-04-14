"""
FastAPI 앱 진입점
================
실행: uvicorn day3.main:app --reload
Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI

from day3.database import engine, Base
from day3.routes import categories, products, orders

# 앱 시작 시 모든 테이블 자동 생성 (이미 존재하면 무시)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 3",
    description="주문 시스템 + 트랜잭션 — Order/OrderItem CRUD",
    version="0.3.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
