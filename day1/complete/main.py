"""
day1/complete/main.py — FastAPI 앱 진입점 (완성형, 줄단위 해설)
================================================================
실행:
    uvicorn day1.complete.main:app --reload
    → http://localhost:8000/docs (Swagger UI)

이 파일은 4가지 일을 한다:
    1) DB 테이블 자동 생성 (create_all)
    2) FastAPI 앱 인스턴스 생성
    3) 라우터 등록 (categories CRUD 5종)
    4) /health 엔드포인트 정의 (DB 연결 헬스체크 포함)
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day1.complete.database import engine, Base, get_db
from day1.complete import models  # noqa: F401  ← Base 메타데이터 등록을 위해 반드시 import
from day1.complete.routes import categories

# Base.metadata.create_all: Base 를 상속한 모든 모델의 테이블이 없으면 만든다.
# 있으면 무시 → 실행을 반복해도 안전.
# Day 5 부터는 Alembic 이 이 역할을 대신하므로 이 줄을 제거한다.
Base.metadata.create_all(bind=engine)

# FastAPI 앱 인스턴스. Swagger UI 의 헤더에 title/description 이 표시된다.
app = FastAPI(
    title="StudyDB Day 1 (Complete)",
    description="CRUD 기초 — Category + 소프트 삭제(is_active) 완성 참고용",
    version="1.0.0",
)

# 라우터 등록. categories.router 는 routes/categories.py 에 정의되어 있다.
app.include_router(categories.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    서버 + DB 연결 상태 확인용 헬스체크.

    db.execute(text("SELECT 1")) 가 성공하면 DB 가 살아있다.
    실패해도 서버 자체는 동작 중일 수 있으므로 status 는 "ok" 로 두고
    db 필드만 connected/disconnected 로 분리한다.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
