# StudyDB 명령어 사전

> Day 1~7 워크북에 등장하는 모든 명령·함수·문법을 카테고리별로 정리한 학습용 레퍼런스.
> **모르는 게 나오면 `Ctrl+F`** — 그게 전부입니다.

---

## 이 문서를 읽는 법

1. **처음 보는 사람**: 위에서 아래로 한 번 훑고 ["1분 치트시트"](#1분-치트시트)를 외우세요.
2. **TODO 풀다 막힌 사람**: 목차에서 해당 카테고리로 점프 → 항목 단위로 검색.
3. **복습하는 사람**: 각 섹션 끝의 **셀프 체크**와 부록의 [Day별 5분 복습 질문](#day별-5분-복습-질문)을 풀어보세요.

각 항목은 다음 마이크로 구조를 따릅니다.

```
### `명령` [Day 표기]
- 역할: 무엇을 하는가
- 시점: 언제 쓰는가
- 예시: 코드 또는 출력
> 주의: 흔히 막히는 지점
```

배지 의미: `[Day1]` 첫 등장 / `[Day5+]` 이후 계속 사용 / `[전 Day]` 매일 사용

---

## Day 1~7 학습 로드맵

| Day | 테마 | 신규 핵심 명령 (요약) | 난이도 |
|-----|------|----------------------|--------|
| 1 | CRUD 기초 | `Column` · `Base.metadata.create_all` · `db.add/commit` · `Depends(get_db)` · `HTTPException` | ★☆☆ |
| 2 | 상품 + 외래키 | `ForeignKey` · `relationship("X", back_populates=...)` · FK 사전 검증 | ★☆☆ |
| 3 | 주문 + 트랜잭션 | `db.flush()` · `db.rollback()` · try/except · `list[XxxResponse]` nested | ★★☆ |
| 4 | 페이지네이션·검색 | `query.count()` · `offset().limit()` · `ilike()` · `getattr` 동적정렬 | ★★☆ |
| 5 | Alembic·인덱스 | `index=True` · `Index()` · `UniqueConstraint` · `alembic upgrade head` | ★★☆ |
| 6 | MES 공정·BOM | 자기참조 FK · `remote_side` · `foreign_keys=[col]` (dual FK) | ★★★ |
| 7 | MES 작업지시·상태 | `@patch` · `func.count/sum/coalesce` · 상태머신 `ALLOWED_TRANSITIONS` | ★★★ |

> 포인트: **각 Day의 완성 코드 = 다음 Day TODO의 정답**입니다. 막히면 다음 Day를 곁눈질하세요.

---

## 1분 치트시트

가장 자주 칠 4종 명령. 이것만 외워도 워크북 70%는 자동입니다.

```bash
# A. DB 컨테이너 기동 (작업 시작)
docker compose up -d

# B. Day 전환 시 DB 완전 초기화 + 재기동
docker compose down -v && docker compose up -d

# C. FastAPI 서버 기동 (StudyDB/ 루트에서 실행!)
uvicorn day1.main:app --reload          # Day 번호만 바꿔가며 재사용

# D. PostgreSQL 셸 진입
docker compose exec db psql -U study -d studydb
```

```bash
# Day 5+ 마이그레이션 한 줄 워크플로
alembic revision --autogenerate -m "변경 설명" && alembic upgrade head
```

```python
# Day 1+ SELECT 한 줄 워크플로 (단건/전체/조건)
db.query(Product).filter(Product.id == 5).first()
db.query(Product).all()
db.query(Product).filter(Product.price >= 100).order_by(Product.price.desc()).all()
```

---

## 목차

1. [쉘 / Docker](#1-쉘--docker)
2. [Python / pip / venv](#2-python--pip--venv)
3. [uvicorn (FastAPI 서버)](#3-uvicorn-fastapi-서버)
4. [Alembic CLI (Day5+)](#4-alembic-cli-day5)
5. [psql / PostgreSQL](#5-psql--postgresql)
6. [SQLAlchemy 모델 정의](#6-sqlalchemy-모델-정의)
7. [SQLAlchemy 세션 / 쿼리](#7-sqlalchemy-세션--쿼리)
8. [FastAPI 라우팅 / 의존성](#8-fastapi-라우팅--의존성)
9. [Pydantic 스키마](#9-pydantic-스키마)
10. [Python 표준 / 유틸](#10-python-표준--유틸)
11. [curl 테스트 명령](#11-curl-테스트-명령)
12. [SQL 매핑 빠른표](#12-sql-매핑-빠른표)

**부록**: [다이어그램](#부록-a-그림으로-보는-핵심-흐름) · [Day별 5분 복습](#day별-5분-복습-질문) · [알파벳 명령 색인](#알파벳-명령-색인) · [자주 막히는 함정 10](#자주-막히는-함정-10)

---

## 1. 쉘 / Docker

### `docker compose up -d` `[전 Day]`
- 역할: `docker-compose.yml`의 PostgreSQL 컨테이너를 백그라운드(`-d` = detached)로 기동.
- 시점: 매일 작업 시작 시 가장 먼저.
- 결과: `localhost:5432`에서 PostgreSQL listening.

### `docker compose down` `[전 Day]`
- 역할: 컨테이너만 정지/삭제. **데이터(볼륨)는 보존**.
- 결과: 다시 `up -d` 시 기존 데이터 유지.

### `docker compose down -v` `[Day 전환]`
- 역할: 컨테이너 + **볼륨까지** 전부 삭제. DB 완전 초기화.
- 시점: Day를 넘어가거나 스키마가 꼬였을 때.

> 주의: `-v` = volumes. 빠지면 데이터 그대로 남습니다.

### `docker compose down -v && docker compose up -d` `[Day 전환]`
- 역할: 완전 초기화 + 빈 DB 재기동. **Day 전환 표준 절차**.

### `docker compose exec db psql -U study -d studydb` `[전 Day]`
- 역할: 실행 중인 `db` 컨테이너 안에서 `psql` 클라이언트 실행.
- 옵션: `-U study` 사용자(=`POSTGRES_USER`), `-d studydb` DB명(=`POSTGRES_DB`).
- 비밀번호: `study1234` (`POSTGRES_PASSWORD`).

### `docker info` `[트러블슈팅]`
- 역할: Docker Desktop 살아있는지 확인.

**셀프 체크 — Docker**

1. `docker compose down`만 실행하고 다시 `up -d` 하면 데이터는 유지될까요? 왜 그럴까요?
2. Day 3에서 Day 4로 넘어갈 때 어떤 한 줄 명령으로 DB를 갈아엎나요?
3. `docker compose exec db psql -U study -d studydb`에서 `-d`의 의미는?

<details>
<summary>정답 보기</summary>

1. 유지됩니다. 컨테이너만 지우고 볼륨(`pgdata`)은 그대로 남기 때문.
2. `docker compose down -v && docker compose up -d` (`-v`가 핵심).
3. `--dbname` 약자. 접속할 데이터베이스 이름 = `studydb`.
</details>

---

## 2. Python / pip / venv

### `python -m venv venv` `[Day1, 1회]`
- 역할: 현재 폴더에 `venv/` 가상환경 생성.
- 이유: 프로젝트별 패키지 격리(시스템 Python 비오염).

### `source venv/Scripts/activate` (Windows Git Bash) `[전 Day]`
- 역할: 가상환경 활성화. 이후 `python`/`pip`은 venv 안의 것을 사용.
- Mac/Linux: `source venv/bin/activate`
- 비활성화: `deactivate`

### `pip install -r requirements.txt` `[Day1, 1회]`
- 역할: `requirements.txt`의 모든 패키지를 한 번에 설치.
- 핵심 패키지: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `pydantic`, `alembic`.

### `pip install psycopg2-binary` `[참고]`
- 역할: PostgreSQL용 Python 드라이버. SQLAlchemy 내부에서 사용.
- `-binary` 버전을 써야 Windows에서 컴파일 오류 없이 설치.

---

## 3. uvicorn (FastAPI 서버)

### `uvicorn day1.main:app --reload` `[전 Day]`
- 역할: ASGI 서버를 띄워 FastAPI 앱을 실행.
- 인자: `day1.main:app` = `day1/main.py` 안의 `app` 변수.
- 옵션: `--reload` 코드 변경 시 자동 재시작 (개발용).
- 접속: http://localhost:8000/docs (Swagger UI).

> 주의: 반드시 **`StudyDB/` 최상위에서** 실행. `day1/` 안에서 실행하면 `ModuleNotFoundError`.

### `uvicorn day1.main:app --reload --port 8001` `[트러블슈팅]`
- 역할: 8000이 점유 중일 때 다른 포트로 실행.

**셀프 체크 — uvicorn**

1. `day1.main:app`의 콜론(`:`)은 무엇을 구분하나요?
2. 왜 `day1/` 폴더 안에서 uvicorn을 실행하면 안 될까요?
3. 8000 포트가 점유 중일 때 어떻게 다른 포트로 바꾸나요?

<details>
<summary>정답 보기</summary>

1. `모듈경로:변수명`. 즉 `day1.main` 모듈의 `app` 객체.
2. import 경로 `day1.xxx` 형태가 깨지면서 `ModuleNotFoundError` 발생.
3. `--port 8001` (또는 8002 등) 추가.
</details>

---

## 4. Alembic CLI (Day5+)

> 비유: **Alembic = "DB 스키마의 git"**. revision = commit, upgrade = checkout.

### `alembic init alembic` `[Day5, 1회]`
- 역할: `alembic/` 폴더 + `alembic.ini` 설정 파일 생성.

### `alembic upgrade head` `[Day5+ 매번]`
- 역할: 미적용 마이그레이션을 모두 최신까지 적용.
- 인자: `head` = 마이그레이션 그래프의 최신 끝점.

> 주의: Day 5 이후 **서버 실행 전에 반드시** 한 번 실행.

### `alembic upgrade +1`
- 역할: 한 단계만 앞으로 적용.

### `alembic downgrade -1`
- 역할: 한 단계 롤백 (이전 revision으로).

### `alembic downgrade base`
- 역할: 모든 마이그레이션 되돌림 → 빈 DB 상태.

### `alembic revision -m "메시지"`
- 역할: **빈** 마이그레이션 파일 생성. `upgrade()`/`downgrade()`를 직접 작성.
- 시점: 데이터 변환, 시퀀스 조정 등 자동감지 불가능한 작업.

### `alembic revision --autogenerate -m "메시지"`
- 역할: `models.py`와 현재 DB 스키마를 비교해 차이를 자동으로 마이그레이션 파일로 생성.
- 시점: 컬럼 추가/삭제, 인덱스 추가 등 단순 스키마 변경.

> 주의: 데이터 변환(예: 컬럼 값 일괄 변경)은 감지 못 합니다. 빈 revision으로 직접 작성하세요.

### `alembic history --verbose`
- 역할: 모든 revision 이력 출력.

### `alembic current`
- 역할: 지금 DB가 어느 revision에 있는지 표시.

### 마이그레이션 파일 안의 `op.*` 함수들 `[Day5 TODO 40]`

| 함수 | 역할 | SQL |
|------|------|-----|
| `op.add_column("products", sa.Column("sku", sa.String(50)))` | 컬럼 추가 | `ALTER TABLE products ADD COLUMN sku VARCHAR(50)` |
| `op.drop_column("products", "sku")` | 컬럼 삭제 | `ALTER TABLE products DROP COLUMN sku` |
| `op.create_index("ix_products_sku", "products", ["sku"], unique=True)` | 유니크 인덱스 생성 | `CREATE UNIQUE INDEX ix_products_sku ON products(sku)` |
| `op.drop_index("ix_products_sku", table_name="products")` | 인덱스 삭제 | `DROP INDEX ix_products_sku` |
| `op.create_unique_constraint("uq_xxx", "products", ["name", "category_id"])` | 복합 유니크 제약 | `ALTER TABLE products ADD CONSTRAINT uq_xxx UNIQUE (name, category_id)` |
| `op.drop_constraint("uq_xxx", "products", type_="unique")` | 제약 삭제 | `ALTER TABLE products DROP CONSTRAINT uq_xxx` |

**셀프 체크 — Alembic**

1. `alembic upgrade head`의 `head`는 어떤 위치를 가리키나요?
2. 컬럼 값을 일괄 변경하고 싶을 때 `--autogenerate`를 써도 되나요?
3. `alembic downgrade -1`과 `alembic downgrade base`의 차이는?

<details>
<summary>정답 보기</summary>

1. 마이그레이션 그래프의 가장 최신 끝점(=가장 최근 revision).
2. 안 됩니다. 데이터 변환은 감지 못하므로 `alembic revision -m "..."`로 빈 파일 만들어 직접 작성.
3. `-1`은 한 단계만 되돌림, `base`는 모든 마이그레이션을 되돌려 빈 DB 상태로.
</details>

---

## 5. psql / PostgreSQL

### 접속
```bash
psql postgresql://study:study1234@localhost:5432/studydb
# 또는 (호스트에 psql 미설치 시)
docker compose exec db psql -U study -d studydb
```

### psql 메타 명령 (`\` 시작)

| 명령 | 역할 |
|------|------|
| `\l` | 데이터베이스 목록 |
| `\dt` | 테이블 목록 |
| `\d 테이블명` | 테이블 구조(컬럼·인덱스·FK) 상세 |
| `\di` | 인덱스 목록 |
| `\du` | 사용자(role) 목록 |
| `\q` | 종료 |
| `\?` | 메타 명령 도움말 |

### 자주 쓰는 SQL

| SQL | 의미 |
|-----|------|
| `SELECT * FROM categories;` | 모든 카테고리 조회 |
| `SELECT * FROM products WHERE category_id = 1;` | 조건 조회 |
| `DROP TABLE IF EXISTS products;` | 테이블 삭제 (Day2 DB 초기화 시) |
| `TRUNCATE TABLE products RESTART IDENTITY CASCADE;` | 테이블 비우기 + id 시퀀스 초기화 |
| `\d products` | products 테이블 구조 확인 |

> 주의: **DROP 순서** — FK가 있는 자식 테이블부터 삭제. 예: `products` → `categories` 순.

---

## 6. SQLAlchemy 모델 정의

### Import 한 줄
```python
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, Float,
    ForeignKey, Index, UniqueConstraint,
)
from sqlalchemy.orm import relationship
```

### `Base = declarative_base()` `[Day1]`
- 역할: 모든 모델 클래스가 상속할 부모 클래스 생성. `database.py`에 1번만.

### `class XXX(Base):` + `__tablename__` `[Day1]`
- 역할: 클래스 1개 = 테이블 1개. `__tablename__`이 실제 DB 테이블 이름.

### `Column(타입, 제약…)` — 컬럼 정의

| 파라미터 | 의미 | SQL |
|---------|------|-----|
| `Integer`, `String(N)`, `Text`, `Boolean`, `DateTime`, `Float` | 컬럼 타입 | `INTEGER`, `VARCHAR(N)`, `TEXT`, `BOOLEAN`, `TIMESTAMP`, `DOUBLE PRECISION` |
| `primary_key=True` | 기본키 | `PRIMARY KEY` |
| `nullable=False` | NULL 금지 | `NOT NULL` |
| `unique=True` | 중복 금지 | `UNIQUE` |
| `default=값` | INSERT 시 기본값 (Python 레벨) | (Python에서 채워서 INSERT) |
| `default=lambda: datetime.now(timezone.utc)` | 호출 시점에 현재 시각 | — |
| `onupdate=lambda: datetime.now(...)` | UPDATE 시 자동 갱신 | — |
| `index=True` | 단일 인덱스 자동 생성 | `CREATE INDEX ix_테이블_컬럼 ON 테이블(컬럼)` |
| `ForeignKey("테이블명.컬럼명")` | 외래키 | `REFERENCES 테이블(컬럼)` |

### 예시 패턴

```python
# 기본키
id = Column(Integer, primary_key=True, index=True)

# 필수 + 유니크 문자열
name = Column(String(100), nullable=False, unique=True)

# 선택 텍스트 (긴 문자열, 길이 제한 없음)
description = Column(Text, nullable=True)

# Boolean + 기본값
is_active = Column(Boolean, nullable=False, default=True)

# 정수 + 기본값 0 (재고)
stock = Column(Integer, nullable=False, default=0)

# 외래키 (1:N의 N쪽)
category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

# 자기참조 외래키 (Day6 Process 트리)
parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)

# 자동 시각
created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
updated_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
)
```

### `relationship()` — ORM 관계 `[Day2+]`

```python
# 1:N 양방향 (Category 1 ─── N Product)
class Category(Base):
    products = relationship("Product", back_populates="category")

class Product(Base):
    category = relationship("Category", back_populates="products")
```

| 파라미터 | 의미 |
|---------|------|
| `"Category"` | 연결할 모델 이름(문자열). 순서 의존 회피를 위해 문자열 권장. |
| `back_populates="xxx"` | 상대 모델의 이 속성과 양방향 연결. 양쪽 이름이 정확히 일치해야 함. |
| `foreign_keys=[col]` | 같은 테이블을 두 번 참조할 때 어떤 FK를 쓸지 명시 (Day6 BOMEntry) |
| `remote_side="Process.id"` 또는 `[id]` | 자기참조 시 "부모 쪽" 컬럼 명시 (Day6 Process) |

```python
# 자기참조 (Day6)
parent = relationship("Process", remote_side="Process.id", back_populates="children")
children = relationship("Process", back_populates="parent")

# 같은 테이블 두 번 참조 (Day6 BOMEntry)
product = relationship("Product", foreign_keys=[product_id])
material = relationship("Product", foreign_keys=[material_id])
```

> 주의: `back_populates` 짝이 안 맞으면 침묵하다 런타임에 터집니다. 양쪽 이름을 정확히 맞추세요.

### `__table_args__` — 테이블 수준 제약 `[Day5]`

```python
class Order(Base):
    __tablename__ = "orders"
    # ... 컬럼 ...
    __table_args__ = (
        Index("ix_orders_customer_created", "customer_name", "created_at"),
        UniqueConstraint("name", "category_id", name="uq_product_name_category"),
    )
```

| 객체 | 역할 | SQL |
|------|------|-----|
| `Index("이름", "col1", "col2", ...)` | 복합 인덱스 | `CREATE INDEX 이름 ON 테이블(col1, col2)` |
| `UniqueConstraint("col1", "col2", name="이름")` | 복합 유니크 | `ALTER TABLE 테이블 ADD CONSTRAINT 이름 UNIQUE (col1, col2)` |

> 주의: **튜플로 감싸기** — 한 개여도 `(... ,)`처럼 콤마 필수.

### `Base.metadata.create_all(bind=engine)` `[Day1~4]`
- 역할: 정의된 모든 모델을 DB 테이블로 만든다 (이미 있으면 스킵).
- 시점: Day 1~4의 `main.py`에서 자동 실행. **Day 5부터는 Alembic이 대신**.

**셀프 체크 — SQLAlchemy 모델**

1. `default=datetime.now(timezone.utc)`와 `default=lambda: datetime.now(timezone.utc)`의 차이는?
2. 같은 테이블을 두 번 참조하는 BOMEntry에서 `foreign_keys=[col]`이 필요한 이유는?
3. `__table_args__`에 항목이 1개일 때 흔히 하는 실수는?

<details>
<summary>정답 보기</summary>

1. 전자는 **모듈 로드 시 한 번만** 평가 → 모든 행이 같은 시각이 됨(잘못된 패턴). 후자는 INSERT 시점마다 람다가 호출되어 각각의 현재 시각.
2. SQLAlchemy가 어느 FK가 어느 relationship에 연결되는지 못 정해서 `AmbiguousForeignKeysError` 발생.
3. 튜플 콤마 누락. `(Index(...))`는 그냥 식이고, `(Index(...),)`이어야 단일 원소 튜플.
</details>

---

## 7. SQLAlchemy 세션 / 쿼리

### 트랜잭션 라이프사이클 한 그림

```
  ┌─────────┐  add()   ┌─────────┐  flush()  ┌─────────┐  commit() ┌──────┐
  │ 메모리만 │ ───────▶ │ 세션 큐 │ ────────▶ │ DB I/O   │ ────────▶│ 영구 │
  │ (객체)  │          │ (대기열)│           │ (PK확보) │          │ 반영 │
  └─────────┘          └─────────┘           └────┬────┘          └──────┘
                                                  │ rollback()
                                                  ▼
                                              ┌──────┐
                                              │ 취소 │ → 이후 세션 재사용 가능
                                              └──────┘
```

### 세션 4대 동작

| 메서드 | 역할 | SQL/시점 |
|--------|------|---------|
| `db.add(obj)` | INSERT 대기열에 추가 | 아직 SQL 실행 안 됨 |
| `db.flush()` | 대기 SQL을 DB로 전송 (트랜잭션 유지). PK 즉시 확보. | `INSERT INTO ...` 실행. commit 전이라 rollback 가능. |
| `db.commit()` | 트랜잭션 확정. 영구 반영. | `COMMIT` |
| `db.rollback()` | 트랜잭션 전체 취소. | `ROLLBACK` |
| `db.refresh(obj)` | DB의 최신 값을 ORM 객체로 다시 읽음 | `SELECT ... WHERE id=?` |
| `db.delete(obj)` | DELETE 대기열에 추가 | `DELETE FROM ...` (commit 시 실행) |
| `db.close()` | 세션 종료 (`get_db()`의 finally가 자동) | — |

### `flush()` vs `commit()` 차이 `[Day3 핵심]`

```python
order = Order(...)
db.add(order)
db.flush()           # ← 여기서 INSERT 실행 → order.id 확보
                     # 하지만 아직 commit 전이라 에러 시 rollback 가능
for item in items:
    db.add(OrderItem(order_id=order.id, ...))   # order.id 사용
db.commit()          # 모든 변경 영구 반영
```

> 주의: PK가 필요한데 commit하면 트랜잭션이 끊깁니다. **PK만 확보**가 목적이면 flush.

### 쿼리 빌더 — `db.query(Model)`

```python
db.query(Product)                                      # SELECT * FROM products
db.query(Product).filter(Product.id == 5)              # WHERE id = 5
db.query(Product).filter(Product.id == 5).first()      # ... LIMIT 1, 결과 1개 또는 None
db.query(Product).all()                                # 전체 결과 list
db.query(Product).count()                              # SELECT COUNT(*) FROM products
```

### 필터 연산자

| Python | SQL | 의미 |
|--------|-----|------|
| `Product.id == 5` | `id = 5` | 등호 |
| `Product.id != 5` | `id <> 5` | 부등호 |
| `Product.price >= 100` | `price >= 100` | 비교 |
| `Product.price <= 500` | `price <= 500` | 비교 |
| `Product.parent_id == None` | `parent_id IS NULL` | NULL 검사 |
| `Product.name.ilike("%저항%")` | `name ILIKE '%저항%'` | 대소문자 무관 부분검색 (PostgreSQL) |
| `Product.name.like("%X%")` | `name LIKE '%X%'` | 대소문자 구분 부분검색 |
| `Product.id.in_([1,2,3])` | `id IN (1,2,3)` | 다중 매칭 |

### 정렬

```python
query.order_by(Product.price)              # ORDER BY price ASC (기본)
query.order_by(Product.price.asc())        # 명시적 오름차순
query.order_by(Product.price.desc())       # ORDER BY price DESC
query.order_by(WorkOrder.created_at.desc())
```

### 페이지네이션 `[Day4]`

```python
total = query.count()                                  # ← offset/limit 적용 전에!
items = query.offset((page - 1) * size).limit(size).all()
```

| 메서드 | SQL |
|--------|-----|
| `query.offset(N)` | `OFFSET N` (앞 N개 건너뜀) |
| `query.limit(N)` | `LIMIT N` (최대 N개) |
| `query.count()` | `SELECT COUNT(*) FROM (...)` |

> 주의: `offset().limit()` 이후에 `count()`를 부르면 **현재 페이지 크기만 셈**. 반드시 페이지네이션 적용 전에.

### 동적 정렬 `[Day4 TODO 32]`

```python
column = getattr(Product, sort_by, None)   # 문자열 → 컬럼 객체
if column is not None:
    query = query.order_by(column.desc() if order == "desc" else column.asc())
```

### 집계 함수 `[Day7 대시보드]`

```python
from sqlalchemy import func

# 그룹별 카운트
db.query(WorkOrder.status, func.count(WorkOrder.id).label("count")) \
  .group_by(WorkOrder.status) \
  .all()
# → [(status='PENDING', count=3), (status='COMPLETED', count=5), ...]

# 합계 + NULL 처리
db.query(func.coalesce(func.sum(WorkOrder.quantity), 0)) \
  .filter(WorkOrder.status == "COMPLETED") \
  .scalar()
# → 단일 값 반환 (행 없으면 0)
```

| 함수 | SQL | 의미 |
|------|-----|------|
| `func.count(X)` | `COUNT(X)` | 개수 |
| `func.sum(X)` | `SUM(X)` | 합계 |
| `func.coalesce(X, 0)` | `COALESCE(X, 0)` | NULL이면 0으로 대체 |
| `.label("alias")` | `AS alias` | 별칭 |
| `.group_by(col)` | `GROUP BY col` | 그룹화 |
| `.scalar()` | — | 단일 값(첫 행 첫 컬럼)만 반환 |

### Raw SQL — `text()`

```python
from sqlalchemy import text
db.execute(text("SELECT 1"))
```
- 임의의 SQL 실행. Day1 헬스체크에서 DB 연결 확인용.

> 주의: 문자열을 그대로 두면 **SQL Injection 위험**. 변수는 `:name` 바인딩 사용 권장.

**셀프 체크 — 세션/쿼리**

1. Day3에서 `db.add(order)` 직후 `order.id`가 비어있는데 자식 OrderItem을 만들어야 합니다. 어떻게?
2. 페이지네이션 코드에서 `count()`는 `offset/limit` 적용 전·후 어디에 와야 하나요?
3. 그룹별 카운트를 구하는 SQL을 SQLAlchemy로 어떻게 표현하나요?

<details>
<summary>정답 보기</summary>

1. `db.flush()` 호출 → INSERT만 먼저 실행되어 `order.id` 확보. 이후 OrderItem 만들고 마지막에 `db.commit()`.
2. **전**. `total = query.count()` 먼저, 그다음 `query.offset(...).limit(...).all()`.
3. `db.query(M.col, func.count(M.id)).group_by(M.col).all()`.
</details>

---

## 8. FastAPI 라우팅 / 의존성

### 요청 → 처리 → 응답 흐름

```
   클라이언트                FastAPI                의존성             핸들러                Pydantic
   ──────────                ───────                ─────              ──────                ────────
   curl/Swagger ─POST/JSON─▶ 라우트 매칭 ──Depends▶ get_db ──Session▶ 함수 본문 ──return──▶ ResponseModel
                              │                                       │                       │
                              │ Body 검증 (422)                       │ HTTPException         │ from_attributes
                              ▼                                       ▼                       ▼
                          PydanticError                        DB 트랜잭션              직렬화 → JSON
```

### 앱 생성
```python
from fastapi import FastAPI
app = FastAPI(title="...", description="...", version="...")
```

### 라우터 분리 (`routes/products.py`)
```python
from fastapi import APIRouter
router = APIRouter(prefix="/products", tags=["products"])
# main.py에서:
app.include_router(router)
```
- `prefix`: 모든 라우트 앞에 자동 추가 (`/products/...`).
- `tags`: Swagger UI에서 그룹핑 라벨.

### 라우트 데코레이터

| 데코레이터 | HTTP 메서드 | 용도 |
|----------|------------|------|
| `@router.get("/")` | GET | 조회 |
| `@router.post("/", status_code=201)` | POST | 생성 |
| `@router.put("/{id}")` | PUT | 전체 수정 |
| `@router.patch("/{id}/start")` | PATCH | 부분 수정/상태 전이 (Day7) |
| `@router.delete("/{id}", status_code=204)` | DELETE | 삭제 |

| 옵션 | 의미 |
|------|------|
| `response_model=ProductResponse` | 응답을 이 Pydantic 스키마로 변환·검증 |
| `response_model=list[ProductResponse]` | 리스트 응답 |
| `status_code=201` | 성공 시 HTTP 상태 코드 (생성=201, 삭제=204) |

### 파라미터 4종

```python
# 1) 경로 파라미터 — URL 경로의 {id}
@router.get("/{product_id}")
def get_product(product_id: int): ...

# 2) 요청 본문(JSON) — Pydantic 모델 타입 힌트
@router.post("/")
def create(data: ProductCreate): ...

# 3) 쿼리 파라미터 — Query()
from fastapi import Query
@router.get("/")
def list_products(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
): ...

# 4) 의존성 — Depends()
from fastapi import Depends
def list_products(db: Session = Depends(get_db)): ...
```

### `Query()` 옵션

| 파라미터 | 의미 |
|---------|------|
| `default=값` | 미전달 시 기본값 |
| `ge=N` | 최소값 (greater or equal) |
| `le=N` | 최대값 |
| `gt=N` / `lt=N` | 초과 / 미만 |
| `description="..."` | Swagger UI 설명문 |

### `Depends(함수)` — 의존성 주입
- 역할: 라우트 실행 직전에 의존 함수를 호출하고 결과를 인자로 주입.
- 핵심 의존성: `Depends(get_db)` → 요청마다 새 DB 세션 생성, 끝나면 자동 close.

### 에러 응답 — `HTTPException`

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="찾을 수 없습니다")
raise HTTPException(status_code=400, detail="재고가 부족합니다")
raise HTTPException(status_code=500, detail="서버 오류")
```

### HTTP 상태코드 (확장표)

| 코드 | 의미 | 사용 예 | 등장 Day |
|------|------|---------|----------|
| 200 | OK | 기본 GET 성공 | Day 1+ |
| 201 | Created | POST 생성 성공 | Day 1+ |
| 204 | No Content | DELETE 성공 (응답 본문 없음) | Day 1+ |
| 400 | Bad Request | 비즈니스 규칙 위반(재고 부족, 상태 전이 불가) | Day 3, 7 |
| 404 | Not Found | 리소스 없음 | Day 1+ |
| 422 | Unprocessable Entity | Pydantic 검증 실패 (자동) | 자동 |
| 500 | Server Error | 예상 못한 예외 | Day 3, 7 |

### try/except + rollback 패턴 `[Day3, Day7]`

```python
try:
    # 여러 단계 작업
    db.commit()
except HTTPException:
    db.rollback()
    raise                          # 의도된 에러는 그대로 전달
except Exception:
    db.rollback()
    raise HTTPException(500, "...")
```

> 주의: rollback 누락 시 세션이 오염되어 **이후 모든 요청이 실패**합니다.

**셀프 체크 — FastAPI**

1. `Depends(get_db)`가 자동으로 처리해주는 두 가지는?
2. 422가 자동으로 발생하는 상황은?
3. `try`에서 `HTTPException`이 떴을 때 한 번 더 `raise`하는 이유는?

<details>
<summary>정답 보기</summary>

1. 요청마다 **새 세션 생성** + 응답 후 **자동 close** (`get_db`의 finally).
2. Pydantic 본문 검증 실패. 예: `int` 자리에 문자열, 필수 필드 누락.
3. 의도된 에러(404/400 등)를 클라이언트에 그대로 전달하기 위해. 안 하면 500이 됨.
</details>

---

## 9. Pydantic 스키마

### 기본 클래스
```python
from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str                                # 필수 문자열
    description: str | None = None           # 선택, 기본 None
    price: int                               # 필수 정수
    stock: int = 0                           # 선택, 기본 0
    category_id: int                         # 필수
```

### 타입 힌트 → 검증 매핑

| 힌트 | 의미 |
|------|------|
| `str` | 문자열 필수 |
| `int` | 정수 필수 |
| `float` | 실수 필수 |
| `bool` | True/False 필수 |
| `datetime` | ISO 8601 문자열 자동 파싱 |
| `str \| None = None` | 선택 (NULL 가능) |
| `int = 0` | 선택, 기본값 0 |
| `list[ProductResponse]` | 리스트 필드 (nested 직렬화) |

### `model_config = {"from_attributes": True}` `[전 Day Response]`
- 역할: ORM 객체(`Product` 인스턴스)의 속성을 자동으로 Pydantic 필드로 매핑.
- 위치: 응답 스키마(`xxxResponse`)에 항상 추가.

> 주의: nested 변환 시 **외부와 내부 스키마 양쪽 모두** 이 설정이 필요 (Day3 OrderResponse + OrderItemResponse).

### nested 스키마 `[Day3]`

```python
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: int
    model_config = {"from_attributes": True}

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    items: list[OrderItemResponse]            # ← relationship이 자동 직렬화됨
    model_config = {"from_attributes": True}
```

### 계산 필드 — 모델에 없는 값 `[Day6, Day7]`

```python
class BOMEntryResponse(BaseModel):
    id: int
    material_id: int
    material_name: str         # ← BOMEntry 모델엔 없음. 라우트에서 수동 주입.
    ...
```

라우트에서:
```python
return BOMEntryResponse(
    id=entry.id,
    material_id=entry.material_id,
    material_name=entry.material.name,   # ← relationship으로 꺼내서 명시 주입
    ...
)
```

### 제네릭 응답 `[Day4 페이지네이션]`

```python
class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list                # 또는 list[ProductResponse]
```

**셀프 체크 — Pydantic**

1. `from_attributes: True`가 없으면 어떤 일이 벌어지나요?
2. 계산 필드(`material_name`)는 모델에 없는데 어떻게 채우나요?
3. `str | None = None`과 `str = ""`의 의미 차이는?

<details>
<summary>정답 보기</summary>

1. ORM → Pydantic 자동 변환 실패. 일일이 `dict()`로 강제 변환해야 함.
2. 라우트에서 명시적으로 `relationship`을 통해 끌어와 `XxxResponse(material_name=entry.material.name, ...)`로 주입.
3. 전자는 NULL/누락 허용(기본값 None), 후자는 항상 빈 문자열로 채워진 필수 흐름.
</details>

---

## 10. Python 표준 / 유틸

### `datetime.now(timezone.utc)`
```python
from datetime import datetime, timezone
datetime.now(timezone.utc)
# → 2026-04-27 14:30:00+00:00 (timezone-aware UTC)
```
- 이 프로젝트 규칙: 모든 시각을 **UTC로 저장**. 클라이언트에서 KST 변환.

### `lambda: datetime.now(timezone.utc)`
- 역할: SQLAlchemy `default=`에 전달할 **함수**. INSERT 시점마다 호출됨.

> 주의: `default=datetime.now(timezone.utc)`처럼 즉시 호출하면 **모듈 로드 시 1번**만 평가 → 모든 행이 같은 시각.

### `getattr(객체, "속성명", 기본값)`
- 역할: 문자열로 속성 동적 접근 `[Day4 동적 정렬]`.
- 예: `getattr(Product, "price", None)` → `Product.price` (없으면 `None`).

### `f"WO-{datetime.now(...).strftime('%Y%m%d%H%M%S')}"`
- 역할: f-string 포매팅 `[Day7 작업지시 번호 생성]`.
- 결과 예: `"WO-20260427143015"`

### `str.upper()` / `str.lower()`
- 대소문자 변환. Day7에서 `status.upper()`로 입력 정규화.

### list comprehension
```python
items = [
    BOMEntryResponse(id=e.id, material_name=e.material.name, ...)
    for e in entries
]
```

---

## 11. curl 테스트 명령

### 기본 형식

```bash
# GET
curl http://localhost:8000/products/

# 쿼리 파라미터
curl "http://localhost:8000/products/?page=1&size=5"

# POST + JSON
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "저항", "price": 50, "stock": 100, "category_id": 1}'

# PUT
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "수정", "price": 60, "stock": 90, "category_id": 1}'

# PATCH (Day7 상태 전이)
curl -X PATCH http://localhost:8000/work-orders/1/start

# DELETE
curl -X DELETE http://localhost:8000/products/1
```

### curl 옵션

| 옵션 | 의미 |
|------|------|
| `-X 메서드` | HTTP 메서드 지정 (POST/PUT/PATCH/DELETE) |
| `-H "헤더"` | 헤더 추가. JSON 보낼 땐 `-H "Content-Type: application/json"` 필수 |
| `-d '본문'` | 요청 본문(주로 JSON) |
| `-s` | silent. 진행률 메시지 숨김 |
| `\| python -m json.tool` | 응답 JSON을 예쁘게 들여쓰기로 출력 |

> 팁: curl 안 쳐도 됩니다. http://localhost:8000/docs 의 **Swagger UI**에서 클릭으로 모든 API를 호출할 수 있습니다.

---

## 12. SQL 매핑 빠른표

### 12-1. CRUD

| 동작 | SQLAlchemy | SQL |
|------|-----------|-----|
| INSERT | `db.add(obj); db.commit()` | `INSERT INTO ... VALUES (...)` |
| SELECT 단건 | `db.query(M).filter(M.id == x).first()` | `SELECT * FROM m WHERE id=x LIMIT 1` |
| SELECT 전체 | `db.query(M).all()` | `SELECT * FROM m` |
| UPDATE | `obj.field = val; db.commit()` | `UPDATE m SET field=val WHERE id=?` |
| DELETE | `db.delete(obj); db.commit()` | `DELETE FROM m WHERE id=?` |

### 12-2. 조건/검색

| Python | SQL |
|--------|-----|
| `.filter(M.x == y)` | `WHERE x = y` |
| `.filter(M.x != y)` | `WHERE x <> y` |
| `.filter(M.x >= y, M.x <= z)` | `WHERE x BETWEEN y AND z` (사실상) |
| `.filter(M.name.ilike("%a%"))` | `WHERE name ILIKE '%a%'` |
| `.filter(M.parent_id == None)` | `WHERE parent_id IS NULL` |
| `.filter(M.id.in_([1,2,3]))` | `WHERE id IN (1,2,3)` |

### 12-3. 페이지네이션 + 정렬

| Python | SQL |
|--------|-----|
| `.order_by(M.x.desc())` | `ORDER BY x DESC` |
| `.offset(10).limit(5)` | `OFFSET 10 LIMIT 5` |
| `.count()` | `SELECT COUNT(*) FROM ...` |

### 12-4. 집계

| Python | SQL |
|--------|-----|
| `db.query(M.status, func.count(M.id)).group_by(M.status)` | `SELECT status, COUNT(id) FROM m GROUP BY status` |
| `func.sum(M.qty)` | `SUM(qty)` |
| `func.coalesce(func.sum(M.x), 0)` | `COALESCE(SUM(x), 0)` |

### 12-5. 스키마

| Python | SQL |
|--------|-----|
| `Column(Integer, primary_key=True)` | `INTEGER PRIMARY KEY` |
| `Column(String(100), nullable=False, unique=True)` | `VARCHAR(100) NOT NULL UNIQUE` |
| `Column(..., index=True)` | + `CREATE INDEX ix_xxx ON ...` |
| `ForeignKey("t.id")` | `REFERENCES t(id)` |
| `Index("ix", "c1", "c2")` | `CREATE INDEX ix ON t(c1, c2)` |
| `UniqueConstraint("c1", "c2", name="uq")` | `UNIQUE (c1, c2)` |

---

## 부록 A. 그림으로 보는 핵심 흐름

### A-1. Day7 상태머신 (작업지시 WorkOrder)

```
   ┌─────────┐  start    ┌─────────┐  complete  ┌───────────┐
   │ PENDING │ ────────▶ │ STARTED │ ─────────▶ │ COMPLETED │
   └────┬────┘           └────┬────┘            └───────────┘
        │ cancel              │ cancel
        ▼                     ▼
   ┌──────────┐          ┌──────────┐
   │ CANCELED │          │ CANCELED │
   └──────────┘          └──────────┘

   허용 전이는 ALLOWED_TRANSITIONS dict로 표현.
   허용되지 않는 전이는 HTTPException(400) 반환.
```

### A-2. Day3 주문 트랜잭션 (다단계 + flush)

```
   POST /orders ──▶ try:
                       db.add(order)        # 큐에 적재
                       db.flush()           # INSERT → order.id 확보
                       for item in items:
                           재고 검증
                           재고 차감
                           db.add(OrderItem(order_id=order.id, ...))
                       db.commit()          # 모두 영구 반영
                    except:
                       db.rollback()        # 전부 무효화
                       raise HTTPException
```

---

## Day별 5분 복습 질문

각 Day가 끝났을 때 5분 안에 풀어보세요. 못 풀면 해당 Day exercises.md로 복귀.

### Day 1 (CRUD 기초)
1. `Depends(get_db)`가 라우트별로 새 세션을 만드는데, 종료는 누가 책임집니까?
2. `text("SELECT 1")`은 무엇을 검증하는 코드인가요?
3. `Column(String(50), nullable=False)`은 SQL로 어떻게 변환되나요?

### Day 2 (외래키 + 관계)
1. `ForeignKey("categories.id")`에 들어가는 문자열은 무엇을 가리키나요?
2. `back_populates="products"`와 `back_populates="category"`가 양쪽에 필요한 이유는?
3. 존재하지 않는 `category_id`로 Product를 만들면 어떤 에러가 나나요? 그 전에 어떻게 사전 검증할 수 있나요?

### Day 3 (트랜잭션)
1. `flush()` 직후·`commit()` 직전에 에러가 발생하면 DB 상태는?
2. nested 응답을 위해 OrderItemResponse에도 `from_attributes`를 켜야 하는 이유는?
3. `HTTPException`을 잡고 다시 `raise`하지 않으면 어떤 응답이 나가나요?

### Day 4 (페이지네이션·검색)
1. 동적 정렬 시 `getattr`을 쓰는 이유는?
2. `ilike`는 PostgreSQL에서만 작동합니까? `like`와의 차이는?
3. `if min_price:`로 0 가격 필터를 거를 때의 함정은?

### Day 5 (Alembic·인덱스)
1. `--autogenerate`가 감지하지 못하는 변경 두 가지를 적어보세요.
2. `Index("ix", "a", "b")`와 `index=True` 두 개 따로 거는 것의 차이는?
3. Day5부터 `create_all()`을 제거하는 이유는?

### Day 6 (자기참조·dual FK)
1. `remote_side`가 가리키는 컬럼은 부모입니까, 자식입니까?
2. BOMEntry에서 `product`와 `material`이 같은 Product 테이블을 참조할 때 무엇이 필요한가요?
3. quantity를 `Float`로 둔 이유는 무엇인가요?

### Day 7 (상태머신·집계)
1. `ALLOWED_TRANSITIONS = {"PENDING": ["STARTED", "CANCELED"], ...}`의 의도는?
2. `func.coalesce(func.sum(...), 0)`을 쓰는 이유는?
3. WorkOrder를 시작할 때 BOM을 보고 자재를 차감하는 트랜잭션은 어디서 한 번에 commit해야 하나요?

---

## 알파벳 명령 색인

| 키워드 / 명령 | 본문 섹션 |
|---------------|-----------|
| `alembic current` | [§4](#4-alembic-cli-day5) |
| `alembic downgrade -1 / base` | [§4](#4-alembic-cli-day5) |
| `alembic history --verbose` | [§4](#4-alembic-cli-day5) |
| `alembic init` | [§4](#4-alembic-cli-day5) |
| `alembic revision --autogenerate` | [§4](#4-alembic-cli-day5) |
| `alembic upgrade head / +1` | [§4](#4-alembic-cli-day5) |
| `Base.metadata.create_all` | [§6](#6-sqlalchemy-모델-정의) |
| `Column` | [§6](#6-sqlalchemy-모델-정의) |
| `Depends` | [§8](#8-fastapi-라우팅--의존성) |
| `db.add / commit / flush / rollback` | [§7](#7-sqlalchemy-세션--쿼리) |
| `db.query` | [§7](#7-sqlalchemy-세션--쿼리) |
| `datetime.now(timezone.utc)` | [§10](#10-python--표준--유틸) |
| `docker compose up -d / down -v` | [§1](#1-쉘--docker) |
| `docker compose exec db psql ...` | [§1](#1-쉘--docker) |
| `f-string` | [§10](#10-python--표준--유틸) |
| `FastAPI()` / `APIRouter` | [§8](#8-fastapi-라우팅--의존성) |
| `ForeignKey` | [§6](#6-sqlalchemy-모델-정의) |
| `func.count / sum / coalesce` | [§7](#7-sqlalchemy-세션--쿼리) |
| `getattr` | [§10](#10-python--표준--유틸) |
| `HTTPException` | [§8](#8-fastapi-라우팅--의존성) |
| `ilike / like / in_` | [§7](#7-sqlalchemy-세션--쿼리) |
| `Index / UniqueConstraint` | [§6](#6-sqlalchemy-모델-정의) |
| `model_config = {"from_attributes": True}` | [§9](#9-pydantic-스키마) |
| `op.add_column / drop_column / create_index` | [§4](#4-alembic-cli-day5) |
| `offset / limit / count` | [§7](#7-sqlalchemy-세션--쿼리) |
| `order_by(col.desc/asc)` | [§7](#7-sqlalchemy-세션--쿼리) |
| `pip install -r requirements.txt` | [§2](#2-python--pip--venv) |
| `psql 메타 명령 \\l \\dt \\d` | [§5](#5-psql--postgresql) |
| `Pydantic BaseModel` | [§9](#9-pydantic-스키마) |
| `Query()` | [§8](#8-fastapi-라우팅--의존성) |
| `relationship / back_populates` | [§6](#6-sqlalchemy-모델-정의) |
| `remote_side` (자기참조) | [§6](#6-sqlalchemy-모델-정의) |
| `text("SELECT 1")` | [§7](#7-sqlalchemy-세션--쿼리) |
| `try/except + rollback` | [§8](#8-fastapi-라우팅--의존성) |
| `uvicorn day1.main:app --reload` | [§3](#3-uvicorn-fastapi-서버) |
| `venv` (`python -m venv`) | [§2](#2-python--pip--venv) |
| `__table_args__` | [§6](#6-sqlalchemy-모델-정의) |
| `__tablename__` | [§6](#6-sqlalchemy-모델-정의) |

---

## 자주 막히는 함정 10

> 실전에서 많이 마주치는 순으로 정렬했습니다.

1. **`ModuleNotFoundError`** — `day1/` 안에서 uvicorn 실행. → `StudyDB/` 루트에서 실행.
2. **`AmbiguousForeignKeysError`** — 같은 테이블 두 번 참조하면서 `foreign_keys=[col]` 누락.
3. **자기참조 시 모호함** — `remote_side` 누락. 부모 쪽 컬럼 명시 필수.
4. **`count()` 위치** — `offset().limit()` 다음에 호출하면 페이지 크기만 셈. **반드시 적용 전**에.
5. **flush vs commit** — PK가 필요한데 commit하면 트랜잭션이 끊김. flush로 PK만 확보.
6. **`if min_price:`** — `0`도 falsy. `if min_price is not None:` 사용.
7. **`default=datetime.now()` (괄호 호출)** — 모듈 로드 시 1번만 평가. 반드시 `default=lambda: datetime.now(...)`.
8. **rollback 누락** — 트랜잭션 중 예외 발생 시 rollback 안 하면 세션 오염, 이후 요청 모두 실패.
9. **`back_populates` 짝 안 맞음** — 양쪽 이름이 정확히 일치해야 함. 한쪽만 바꾸면 침묵하다 런타임에 터짐.
10. **DROP 순서** — FK 참조하는 자식 테이블부터 DROP. 부모 먼저 DROP하면 제약 위반.

---

> 마지막 팁: 이 문서를 한 번에 다 외우려 하지 마세요.
> Day 1을 풀면서 §1·§3·§6·§7만, Day 5에 들어가면 §4·`Index`·`UniqueConstraint`만,
> 이런 식으로 **Day별 필요분만 골라 외우는 게** 가장 빠릅니다.
