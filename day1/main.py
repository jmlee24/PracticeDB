"""
FastAPI 앱 진입점
================
실행: uvicorn day1.main:app --reload
Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day1.database import engine, Base, get_db
from day1.routes import categories

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 1",
    description="CRUD 기초 - 카테고리 관리 API",
    version="0.1.0",
)

app.include_router(categories.router)


@app.get("/health")
def health_check(
    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 1] DB 연결 상태 확인 추가                    │
    # │                                                    │
    # │ 현재 health_check는 단순히 {"status": "ok"}만     │
    # │ 반환합니다. DB가 실제로 연결되어 있는지도          │
    # │ 확인하도록 수정하세요.                             │
    # │                                                    │
    # │ 조건:                                              │
    # │ 1. 함수 시그니처에 db: Session = Depends(get_db)   │
    # │    파라미터 추가                                   │
    # │ 2. db.execute(text("SELECT 1"))로 DB 연결 확인     │
    # │ 3. 성공 시: {"status": "ok", "db": "connected"}    │
    # │ 4. 실패 시: {"status": "ok", "db": "disconnected"} │
    # │                                                    │
    # │ 힌트:                                              │
    # │   try:                                             │
    # │       db.execute(text("SELECT 1"))                 │
    # │       db_status = "connected"                      │
    # │   except Exception:                                │
    # │       db_status = "disconnected"                   │
    # │   return {"status": "ok", "db": db_status}         │
    # └──────────────────────────────────────────────────┘
):
    """서버 상태 확인"""
    return {"status": "ok"}
