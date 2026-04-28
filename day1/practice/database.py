"""
day1/practice/database.py — DB 연결 (이 파일은 그대로 사용, 수정 X)
================================================================
이 파일은 보고만 두세요. database 설정은 실습 범위가 아닙니다.
같은 패턴이 day1/complete/database.py 에도 있으니 비교해서 읽으면 좋습니다.
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
