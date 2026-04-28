"""
day1/complete/models.py — Category 모델 (완성형, 줄단위 해설)
================================================================
ORM(Object-Relational Mapping) 의 약속:
    파이썬 클래스 1개 = DB 테이블 1개
    클래스 인스턴스 1개 = 테이블의 행(row) 1개
    클래스 필드(Column) 1개 = 테이블의 컬럼 1개

이 파일은 'categories' 테이블 1개를 정의한다.
컬럼별로 SQL 문법으로 어떻게 변환되는지 한 줄씩 주석으로 매핑해두었다.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime, timezone

from day1.complete.database import Base


class Category(Base):
    """
    카테고리 테이블 — 상품 분류용.

    이 클래스의 Column 7개가 그대로 categories 테이블의 컬럼이 된다.
    Base.metadata.create_all(bind=engine) 호출 시 아래와 동등한 SQL이 실행된다:

        CREATE TABLE categories (
            id          INTEGER     PRIMARY KEY,
            name        VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            is_active   BOOLEAN      NOT NULL,
            created_at  TIMESTAMP
        );
        CREATE INDEX ix_categories_id ON categories(id);
    """
    __tablename__ = "categories"  # → 실제 DB 테이블명. 클래스명(Category)과 다를 수 있다.

    # Integer + primary_key=True → INTEGER PRIMARY KEY (자동 시퀀스)
    # index=True → CREATE INDEX ix_categories_id ON categories(id)
    id = Column(Integer, primary_key=True, index=True)

    # String(100) → VARCHAR(100). 길이 제한 있는 가변 문자열.
    # nullable=False → NOT NULL. INSERT 시 반드시 값이 있어야 함.
    # unique=True → UNIQUE 제약. 같은 name 두 번 INSERT 시 IntegrityError.
    name = Column(String(100), nullable=False, unique=True)

    # Text → TEXT. 길이 제한 없는 긴 문자열. 기본 nullable=True (없어도 됨).
    description = Column(Text, nullable=True)

    # Boolean → BOOLEAN. True/False만 가능.
    # default=True → 파이썬 레벨 기본값. INSERT 시 값을 안 주면 True 로 저장.
    # 이 컬럼은 "소프트 삭제" 패턴에 쓰인다:
    #   삭제하지 않고 is_active=False 로 비활성화 → 복구 가능.
    is_active = Column(Boolean, nullable=False, default=True)

    # DateTime → TIMESTAMP.
    # default=lambda: ... → INSERT 시점에 람다가 호출되어 현재 UTC 시각 저장.
    # 주의: default=datetime.now(timezone.utc) (괄호 호출) 로 쓰면
    #      모듈 로드 시점에 1번만 평가되어 모든 행이 같은 시각이 된다.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
