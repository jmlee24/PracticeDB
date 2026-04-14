"""
FastAPI 앱 진입점
================
실행: uvicorn day4.main:app --reload
Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI

from day4.database import engine, Base
from day4.routes import categories, products, orders

# 앱 시작 시 모든 테이블 자동 생성 (이미 존재하면 무시)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 4",
    description="페이지네이션 + LIKE 검색 + 동적 정렬",
    version="0.4.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
