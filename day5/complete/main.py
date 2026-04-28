"""
day5/complete/main.py — Alembic 시대의 main.py
================================================================
Day 5 부터는 Base.metadata.create_all 을 호출하지 않는다!
테이블 생성/변경은 Alembic 이 담당:

    cd day5/complete
    alembic upgrade head

서버 실행 전에 반드시 alembic upgrade head 가 1회 이상 실행되어야 한다.
"""
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from day5.complete.database import get_db
from day5.complete import models  # noqa: F401  ← Base 메타데이터 등록 (Alembic 도 사용)
from day5.complete.routes import categories, products, orders

# Base.metadata.create_all(bind=engine)   ← 의도적으로 주석. Alembic 이 대신.

app = FastAPI(
    title="StudyDB Day 5 (Complete)",
    description="Alembic 마이그레이션 + 인덱스/유니크 제약 완성 참고용",
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "db": db_status}
