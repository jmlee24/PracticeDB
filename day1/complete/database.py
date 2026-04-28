"""
day1/complete/database.py — DB 연결 설정 (완성형, 줄단위 해설)
================================================================
이 파일은 SQLAlchemy로 PostgreSQL에 연결하기 위한 4개의 핵심 객체를 만든다.

1) engine        — DB와의 실제 TCP 연결 풀을 관리. 앱 전체에서 1개만 만든다.
2) SessionLocal  — 요청마다 짧게 살아있는 "트랜잭션 컨텍스트"를 찍어내는 팩토리.
3) Base          — 모든 모델 클래스가 상속할 부모. SQLAlchemy 메타데이터의 뿌리.
4) get_db()      — FastAPI Depends() 에 주입할 제너레이터. 요청 종료 시 close 보장.

처음 실행하면 PostgreSQL에 'studydb' DB가 비어있는 상태로 접속한다.
테이블은 main.py 의 Base.metadata.create_all(bind=engine) 가 만든다.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DB 접속 문자열: postgresql://<user>:<password>@<host>:<port>/<db_name>
# docker-compose.yml 의 POSTGRES_USER/PASSWORD/DB 와 정확히 일치해야 한다.
DATABASE_URL = "postgresql://study:study1234@localhost:5432/studydb"

# create_engine: 커넥션 풀 생성. 앱 라이프사이클 동안 단 한 번만 만든다.
# 이 한 줄이 실제 TCP 연결을 즉시 여는 것은 아니고, 첫 쿼리 시 lazy 하게 연다.
engine = create_engine(DATABASE_URL)

# sessionmaker: 세션(=ORM 트랜잭션)을 찍어내는 팩토리.
# - autocommit=False: 명시적으로 db.commit() 을 호출해야만 트랜잭션 확정.
# - autoflush=False : 쿼리 직전 자동 flush 끔. flush 타이밍을 코드에서 직접 제어.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base: 이 Base 를 상속한 모든 클래스가 "테이블 정의"로 등록된다.
# Base.metadata 가 모든 테이블 정보를 모은다 → main.py 에서 create_all 시 사용.
Base = declarative_base()


def get_db():
    """
    FastAPI Depends(get_db) 로 주입되는 세션 제너레이터.

    동작 흐름:
        요청 도착 → SessionLocal() 호출 → yield db 가 라우트로 전달 →
        라우트 본문 실행 → 응답 반환 직전 finally 진입 → db.close() 로 커넥션 반납.

    이 패턴 덕분에 라우트 함수는 close 를 신경쓸 필요가 없다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
