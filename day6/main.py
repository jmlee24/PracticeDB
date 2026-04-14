"""
FastAPI 앱 진입점
================
실행: uvicorn day6.main:app --reload
Swagger UI: http://localhost:8000/docs

Day 6: MES 공정 + BOM 워크북
- 기존: categories, products, orders
- 신규: processes (공정 트리), bom (자재명세서)
"""
from fastapi import FastAPI

from day6.database import engine, Base
from day6.routes import categories, products, orders, processes, bom

# Day 5(Alembic)와 달리 Day 6는 create_all로 테이블 자동 생성
# Alembic 없이 빠르게 실습 환경을 구성하기 위해 사용
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 6",
    description="MES 공정 + BOM 워크북 — Process 트리 + BOMEntry",
    version="0.6.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(processes.router)
app.include_router(bom.router)


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}
