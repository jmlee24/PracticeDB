"""
Day 5: Alembic 마이그레이션
==========================
주의: create_all()이 제거되었습니다!
서버 실행 전에 반드시 `alembic upgrade head`를 먼저 실행하세요.

실행 순서:
  1. cd day5
  2. alembic upgrade head   ← 테이블 생성
  3. uvicorn day5.main:app --reload  (다른 터미널)

Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI

from day5.routes import categories, products, orders

# Base.metadata.create_all(bind=engine)  ← 제거됨! Alembic이 스키마 관리

app = FastAPI(
    title="StudyDB Day 5",
    description="Alembic 마이그레이션 + 인덱스",
    version="0.1.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
