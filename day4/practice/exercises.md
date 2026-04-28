# Day 4 / practice — 페이지네이션 + 재고 범위 필터 변형 문제

## 변형 매핑

| complete (`list_products`) | practice (`list_items`) |
|----------|----------|
| `search` | `keyword` |
| `min_price` / `max_price` | `min_stock` / `max_stock` |
| `Product.price >= ...` 비교 | `Item.stock >= ...` 비교 |
| 정렬 컬럼 후보: id/name/price/stock | 동일 |

## TODO

| # | 파일 | 내용 |
|---|------|------|
| 1 | `routes/items.py` | 통합 `list_items` 8개 쿼리 파라미터 + count/offset/limit |
| 2 | `routes/bookings.py` | `list_bookings` 페이지네이션 + status 필터 |

## 환경 세팅

```bash
docker compose down -v && docker compose up -d
uvicorn day4.practice.main:app --reload

# 테스트 데이터 (10개 정도)
for i in 1 2 3 4 5; do
  curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
    -d "{\"name\":\"상품$i\",\"price\":$((i*1000)),\"stock\":$((i*10)),\"brand_id\":1}"
done
```

## 검증

```bash
# 페이지네이션
curl "http://localhost:8000/items/?page=1&size=3"
# 기대: total=10, page=1, size=3, items 3개

# 재고 범위 필터 (min_stock=20, max_stock=40)
curl "http://localhost:8000/items/?min_stock=20&max_stock=40"
# 기대: 재고 20~40 인 것만

# 0재고 필터 — 함정 검증 (if min_stock: 가 잘못이면 0 이 무시됨)
curl "http://localhost:8000/items/?min_stock=0&max_stock=0"
# 기대: 재고 0 인 것만 (0 이 falsy 라서 필터 안되면 버그)

# 키워드 + 정렬 + 페이지
curl "http://localhost:8000/items/?keyword=상품&sort_by=stock&order=desc&page=1&size=5"
```

## 함정

1. **`if min_stock:` ≠ `if min_stock is not None:`**
   `0` 도 유효한 재고 값이므로 `is not None` 으로 비교해야 한다.

2. **`count()` 위치**
   ```python
   # 잘못
   items = query.offset(...).limit(...).all()
   total = query.count()  # ← 페이지 크기만 셈! 잘못된 total

   # 올바름
   total = query.count()  # ← 필터 후 전체
   items = query.offset(...).limit(...).all()
   ```

3. **`getattr` 의 None 체크**
   잘못된 `sort_by` 값(예: `"이름"`) 이 와도 None 으로 안전하게 정렬 생략.

## 참고
- complete 의 `routes/products.py` `list_products` 함수가 정답 템플릿.
- complete 의 `routes/orders.py` `list_orders` 가 TODO 2 의 템플릿.
