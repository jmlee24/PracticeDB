"""
day1/practice/main.py — FastAPI 앱 (이 파일은 그대로 사용, 수정 X)
================================================================
실행:
    uvicorn day1.practice.main:app --reload --port 8001
    → http://localhost:8001/docs

complete 와 동시에 띄우려면 포트가 달라야 한다 (--port 8001).
또는 트랙을 바꿀 때마다 docker compose down -v && up -d 로 DB 초기화.
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day1.practice.database import engine, Base, get_db
from day1.practice import models  # noqa: F401
from day1.practice.routes import categories

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Day 1 (Practice)",
    description="CRUD 기초 실습 — Category + 노출 토글(is_published) 변형 문제",
    version="1.0.0",
)

app.include_router(categories.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """서버 + DB 헬스체크. complete 와 동일한 패턴 — 그대로 둔다."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
