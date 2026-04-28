"""
day2/complete/database.py — DB 연결 (Day1과 동일, 트랙별로 1개씩 보유)
================================================================
같은 코드를 Day마다 복사해두는 이유: 각 Day가 독립 학습 단위라서
다른 Day의 코드를 안 봐도 그 Day 안에서 완결되도록 하기 위함.
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
