"""
FastAPI 앱 진입점
================
이 파일은 완성된 코드입니다.

실행 방법:
  1. docker compose up -d          (PostgreSQL 실행)
  2. pip install -r requirements.txt
  3. uvicorn phase1.main:app --reload

실행 후 브라우저에서:
  - http://localhost:8000/docs   → Swagger UI (API 테스트 가능)
  - http://localhost:8000/health → 헬스체크
"""

from fastapi import FastAPI

from phase1.database import engine, Base
from phase1.routes import categories, products

# 앱이 시작될 때 모든 모델의 테이블을 자동 생성
# 이미 존재하면 무시함 (개발용. 운영에서는 마이그레이션 도구 사용)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudyDB Phase 1",
    description="제품/재고 관리 API - DB + 백엔드 연동 연습",
    version="0.1.0",
)

# 라우터 등록
# include_router로 각 라우트 파일의 엔드포인트를 앱에 연결
app.include_router(categories.router)
app.include_router(products.router)


@app.get("/health")
def health_check():
    """서버가 살아있는지 확인하는 엔드포인트"""
    return {"status": "ok"}
