"""
day2/complete/models.py — Category 1:N Product (완성형, 줄단위 해설)
================================================================
Day 2 의 핵심: 외래키(ForeignKey) + 양방향 relationship.

테이블 관계:
    categories (1) ─────< products (N)
    하나의 Category 에 여러 Product 가 속한다.

DB 레벨 보장:
    products.category_id 가 categories.id 를 참조 (FK 제약).
    DB 가 존재하지 않는 category_id 삽입을 자동 차단.

ORM 레벨 편의:
    relationship() 으로 Python 객체 그래프 탐색.
    category.products → 그 카테고리의 상품 목록
    product.category  → 그 상품의 카테고리
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from day2.complete.database import Base


class Category(Base):
    """카테고리 테이블 — Day 1 모델 + relationship 한 줄 추가."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # relationship: ORM 레벨에서 "이 카테고리에 속한 상품 목록" 을 자동으로 가져옴.
    # "Product"      → 연결할 클래스 이름 (문자열로 써서 forward ref 안전)
    # back_populates → 상대(Product) 의 'category' 속성과 양방향 연결
    # 이 줄은 DB에 컬럼을 만들지 않는다. 순수 파이썬 객체 탐색용.
    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    상품 테이블 — Category 의 자식.

    SQL 변환:
        CREATE TABLE products (
            id           INTEGER PRIMARY KEY,
            name         VARCHAR(200) NOT NULL,
            description  TEXT,
            price        INTEGER NOT NULL,
            stock        INTEGER NOT NULL DEFAULT 0,
            category_id  INTEGER NOT NULL REFERENCES categories(id),
            created_at   TIMESTAMP,
            updated_at   TIMESTAMP
        );
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Integer 가격. 원 단위로 정수 저장 (소수점 환율은 별 테이블에서 관리하는 게 보통).
    price = Column(Integer, nullable=False)

    # default=0 → INSERT 시 stock 미전달이면 0. 음수 방지는 비즈니스 로직(라우트)에서.
    stock = Column(Integer, nullable=False, default=0)

    # ForeignKey("categories.id") → REFERENCES categories(id)
    # 외래키는 "참조 무결성" 제약. 존재하지 않는 category_id 로 INSERT 시 IntegrityError.
    # nullable=False → 모든 상품은 반드시 카테고리가 있어야 함.
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # onupdate → UPDATE 문 실행 시 SQLAlchemy 가 자동으로 람다 호출해 새 값 채움
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 양방향 relationship 의 반대편.
    # back_populates="products" 가 Category.products 와 짝이 되어야 한다.
    # 두 이름이 1글자라도 다르면 침묵하다 런타임에 깨진다.
    category = relationship("Category", back_populates="products")
