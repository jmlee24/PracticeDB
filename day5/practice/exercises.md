# Day 5 / practice — Alembic + barcode/UQ 변형 문제

## 변형 매핑

| complete | practice |
|----------|----------|
| `Product.name` index=True | `Item.name` index=True |
| `Order.status` index=True | `Booking.status` index=True |
| `Index(customer_name, created_at)` on Order | 같은 인덱스 on Booking |
| `UniqueConstraint(name, category_id)` | `UniqueConstraint(name, brand_id)` |
| (없음) | **`Item.barcode` 컬럼 + unique 인덱스 신규 추가** |

## TODO 8개

| # | 파일 | 내용 |
|---|------|------|
| 1 | `models.py` | `Item.name` 에 `index=True` |
| 2 | `models.py` | `Item.barcode = Column(String(50), nullable=True, unique=True)` |
| 3 | `models.py` | `Item.__table_args__` 에 `UniqueConstraint(name, brand_id)` |
| 4 | `models.py` | `Booking.status` 에 `index=True` |
| 5 | `models.py` | `Booking.__table_args__` 에 `Index(...)` |
| 6 | `schemas.py` | `ItemCreate.barcode: str \| None = None` |
| 7 | `schemas.py` | `ItemResponse.barcode: str \| None` |
| 8 | `routes/items.py` | `create_item` 에 `barcode=data.barcode` 한 줄 |

## 환경 세팅 (Day 5 전용)

```bash
# 1) DB 완전 초기화 (이전 트랙의 스키마 잔존 방지)
docker compose down -v && docker compose up -d

# 2) practice 폴더로 이동
cd day5/practice

# 3) 마이그레이션 자동 생성 (TODO 모두 완성 후)
alembic revision --autogenerate -m "초기 스키마 + barcode + 복합UQ"

# 4) 적용
alembic upgrade head

# 5) 서버 (StudyDB 루트로 돌아가)
cd ../..
uvicorn day5.practice.main:app --reload
```

## 검증

```bash
# barcode 가 실제 저장되는지
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
  -d '{"name":"테스트","price":100,"stock":1,"brand_id":1,"barcode":"880001"}'
# 기대: 응답 JSON 에 barcode: "880001"

# 같은 barcode 중복 → 409 또는 IntegrityError (DB가 자동 거절)
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
  -d '{"name":"중복바코드","price":100,"stock":1,"brand_id":1,"barcode":"880001"}'

# 같은 brand 안에서 같은 이름 중복 → IntegrityError (UQ 제약)
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
  -d '{"name":"테스트","price":200,"stock":1,"brand_id":1}'
# 다른 brand 면 OK

# 인덱스 확인 (psql)
docker compose exec db psql -U study -d studydb -c "\di"
# 기대: ix_items_name, ix_bookings_status, ix_bookings_customer_created,
#       uq_item_name_brand, items_barcode_key 등이 보여야 함
```

## 함정

1. **`__table_args__` 끝 콤마**: `(UniqueConstraint(...))` 는 단순 식이고 `(UniqueConstraint(...),)` 이어야 단일 원소 튜플.
2. **autogenerate 의 한계**: 컬럼 값 변환은 감지 못함. `alembic revision -m "..."` 로 빈 파일 만들어 직접 작성.
3. **순서**: alembic upgrade 먼저, 서버 기동은 그 다음.

## 참고
- complete 의 `models.py` 전체가 패턴 템플릿.
- complete 의 `alembic/env.py` 와 거의 동일 (import 경로만 day5.practice).
