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

# PostgreSQL 접속 URL
# 형식: postgresql://유저:비밀번호@호스트:포트/DB이름
DATABASE_URL = "postgresql://study:study1234@localhost:5432/studydb"

# Engine 생성
# - DB 커넥션 풀을 내부적으로 관리함
# - 앱 전체에서 하나만 만들어서 재사용
engine = create_engine(DATABASE_URL)

# 세션 팩토리
# - autocommit=False: 명시적으로 commit() 해야 반영됨
# - autoflush=False: flush도 수동으로 제어
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 부모 클래스
Base = declarative_base()


def get_db():
    """
    FastAPI 라우트에서 DB 세션을 주입받기 위한 의존성 함수.

    사용법 (라우트에서):
        @router.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...

    yield 이후의 코드는 요청이 끝난 후 항상 실행됨 (finally와 같은 역할)
    → DB 세션이 반드시 닫히도록 보장
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
