# Day 5 워크북 — Alembic 마이그레이션 + 인덱스

## 환경 세팅 (Day 5 전용 순서)

> **주의**: Day 5는 `alembic upgrade head`를 서버 실행 전에 반드시 먼저 실행해야 합니다.

```bash
# 1. DB 초기화 (볼륨 포함 완전 재시작)
docker compose down -v && docker compose up -d

# 2. day5 폴더로 이동
cd day5

# 3. Alembic으로 초기 테이블 생성 (create_all 대신!)
alembic upgrade head

# 4. 서버 실행 (다른 터미널에서)
uvicorn day5.main:app --reload

# 5. Swagger UI 확인
# http://localhost:8000/docs
```

---

## TODO 목록

| #  | 난이도 | 종류 | 설명 |
|----|--------|------|------|
| 35 | ★☆☆   | 코드 | `Product.name`에 `index=True` 추가 |
| 36 | ★☆☆   | 코드 | `Order.status`에 `index=True` 추가 |
| 37 | ★★☆   | 코드 | `Order`에 복합 인덱스 `__table_args__` 추가 |
| 38 | ★★☆   | 코드 | `Product`에 복합 유니크 제약 추가 |
| 39 | ★★☆   | CLI  | `autogenerate`로 마이그레이션 파일 생성 |
| 40 | ★★★   | CLI  | 수동 마이그레이션으로 `sku` 컬럼 추가 |
| 41 | ★★★   | CLI  | `downgrade` → `upgrade` → `history` 확인 |

---

## TODO 35 해설 — Product.name 단일 인덱스 (★☆☆)

`models.py`에서 `Product.name` 컬럼을 찾아 `index=True`를 추가합니다.

```python
# 변경 전
name = Column(String(200), nullable=False)

# 변경 후
name = Column(String(200), nullable=False, index=True)
```

**왜 필요한가?**
`SELECT * FROM products WHERE name = '...'` 같은 쿼리는 인덱스가 없으면
테이블 전체를 순차 스캔(O(n))합니다. `index=True`를 추가하면 PostgreSQL이
B-Tree 인덱스를 생성해 O(log n)으로 탐색합니다.

---

## TODO 36 해설 — Order.status 단일 인덱스 (★☆☆)

```python
# 변경 전
status = Column(String(20), nullable=False, default="pending")

# 변경 후
status = Column(String(20), nullable=False, default="pending", index=True)
```

**왜 필요한가?**
주문 상태별 조회(`WHERE status = 'pending'`)는 실무에서 매우 빈번합니다.
상태 값의 종류가 적어도(카디널리티가 낮아도) 인덱스가 유효한 경우가 많습니다.

---

## TODO 37 해설 — Order 복합 인덱스 (★★☆)

`models.py`의 `Order` 클래스 안에 `__table_args__`를 추가합니다.

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Index
# ...

class Order(Base):
    __tablename__ = "orders"
    # ... 컬럼 정의 ...

    # 복합 인덱스: 고객명 + 생성일 기준 조회 최적화
    __table_args__ = (
        Index("ix_orders_customer_created", "customer_name", "created_at"),
    )

    items = relationship("OrderItem", back_populates="order")
```

**왜 필요한가?**
`WHERE customer_name = '홍길동' AND created_at > '2024-01-01'` 처럼
두 컬럼을 함께 필터링할 때 단일 인덱스 두 개보다 복합 인덱스 하나가 더 효율적입니다.

---

## TODO 38 해설 — Product 복합 유니크 제약 (★★☆)

`models.py`의 `Product` 클래스 안에 `__table_args__`를 추가합니다.

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
# ...

class Product(Base):
    __tablename__ = "products"
    # ... 컬럼 정의 ...

    # 같은 카테고리 내 상품명 중복 방지
    __table_args__ = (
        UniqueConstraint("name", "category_id", name="uq_product_name_category"),
    )

    category = relationship("Category", back_populates="products")
```

**왜 필요한가?**
`name` 단독 유니크는 너무 엄격합니다(다른 카테고리에 같은 이름 허용 불가).
복합 유니크는 `(name, category_id)` 쌍이 중복될 때만 오류를 냅니다.

---

## TODO 39 — autogenerate 마이그레이션 (★★☆, CLI)

TODO 35~38을 모두 완료한 뒤 실행합니다.

```bash
# day5/ 폴더에서 실행
alembic revision --autogenerate -m "add indexes"
```

**확인 포인트**
- `alembic/versions/` 아래 새 파일이 생성되었는지 확인
- 생성된 파일의 `upgrade()` 함수 안에 `create_index`, `create_unique_constraint` 구문이 있는지 확인
- `downgrade()` 함수 안에 반대 구문(`drop_index`, `drop_constraint`)이 있는지 확인

```bash
# 마이그레이션 적용
alembic upgrade head
```

---

## TODO 40 — 수동 마이그레이션: sku 컬럼 추가 (★★★, CLI)

autogenerate를 쓰지 않고 직접 마이그레이션 파일을 작성합니다.

```bash
# 빈 마이그레이션 파일 생성
alembic revision -m "add product sku"
```

생성된 파일(`alembic/versions/xxxx_add_product_sku.py`)을 열어 수정합니다.

```python
def upgrade() -> None:
    # products 테이블에 sku 컬럼 추가
    op.add_column(
        "products",
        sa.Column("sku", sa.String(50), nullable=True),
    )
    # sku에 유니크 인덱스 추가
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)


def downgrade() -> None:
    # 롤백: 인덱스와 컬럼을 순서대로 제거
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_column("products", "sku")
```

```bash
# 적용
alembic upgrade head
```

**포인트**: autogenerate는 모델 변경을 감지하지만, 수동 마이그레이션은
데이터 변환, 시퀀스 조정 등 autogenerate가 처리 못하는 작업에 사용합니다.

---

## TODO 41 — downgrade / upgrade / history (★★★, CLI)

```bash
# 한 단계 롤백
alembic downgrade -1

# 재적용
alembic upgrade head

# 마이그레이션 이력 확인
alembic history --verbose

# 현재 적용된 버전 확인
alembic current
```

**확인 포인트**
- `alembic history`에 지금까지 생성한 revision이 모두 나타나는지 확인
- `alembic current`가 최신 head를 가리키는지 확인
- downgrade 후 psql로 접속해 인덱스/컬럼이 실제로 사라졌는지 확인

```bash
# psql로 인덱스 목록 확인
psql postgresql://study:study1234@localhost:5432/studydb -c "\di"
```

---

## 핵심 개념

### 마이그레이션 = DB 스키마의 git

| git        | Alembic           |
|------------|-------------------|
| commit     | revision          |
| checkout   | upgrade / downgrade |
| log        | history           |
| HEAD       | head              |

스키마 변경 이력을 코드로 관리하므로 팀원 간 DB 상태를 동기화할 수 있습니다.

### B-Tree 인덱스 — O(log n)

```
인덱스 없음: 테이블 전체 스캔 → O(n)
인덱스 있음: B-Tree 탐색      → O(log n)

행 수 100만 기준:
- 순차 스캔: 최대 100만 번 비교
- B-Tree:    최대 20번 비교 (log₂ 1,000,000 ≈ 20)
```

### autogenerate vs 수동 마이그레이션

| 상황 | 방법 |
|------|------|
| 모델 변경(컬럼 추가/삭제, 인덱스) | `--autogenerate` |
| 데이터 마이그레이션 (값 변환) | 수동 작성 |
| 시퀀스, 함수, 뷰 등 비표준 객체 | 수동 작성 |
| autogenerate가 감지 못하는 변경 | 수동 작성 |

---

## 검증 체크리스트

- [ ] `alembic upgrade head` 실행 후 오류 없이 완료되는가?
- [ ] `http://localhost:8000/docs`에서 모든 엔드포인트가 정상 작동하는가?
- [ ] TODO 35~38 완료 후 `alembic revision --autogenerate`가 인덱스 변경을 감지하는가?
- [ ] `alembic downgrade -1` 후 인덱스가 DB에서 사라지는가?
- [ ] `alembic upgrade head` 재실행 후 인덱스가 복원되는가?

---

## 참고

> **Alembic은 여기서 핵심만 다룹니다.**
> 실무에서는 공식 튜토리얼([alembic.sqlalchemy.org](https://alembic.sqlalchemy.org))로
> 심화 학습하세요. 특히 branch, merge, 환경별 설정 분리를 다루는 섹션이 중요합니다.

---

## 다음 단계

**Day 6**: MES 공정 + BOM (Bill of Materials)
- 다대다 관계 심화
- 재귀적 자기 참조 모델
- 공정 순서와 의존성 관리