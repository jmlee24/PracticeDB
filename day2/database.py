"""
데이터베이스 연결 설정
====================
이 파일은 완성된 코드입니다. 읽고 이해하세요.

핵심 개념:
- Engine: DB와의 실제 연결을 관리하는 객체
- SessionLocal: 요청마다 독립적인 DB 세션을 생성하는 팩토리
- Base: 모든 모델(테이블)이 상속하는 부모 클래스
- get_db(): FastAPI의 Dependency Injection에 사용되는 제너레이터
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://study:study1234@localhost:5432/studydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
