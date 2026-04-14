# Day 4 — 페이지네이션 + 검색 + 정렬 워크북

## 핵심 개념

### offset/limit 페이지네이션
```
전체 25건, page=2, size=10 이라면:
  offset = (2 - 1) * 10 = 10  → 11번째 행부터
  limit  = 10                  → 10건만 가져옴
  SQL: SELECT * FROM products OFFSET 10 LIMIT 10
```

### ilike() — 대소문자 무관 부분검색
```python
Product.name.ilike(f"%{search}%")
# SQL: WHERE name ILIKE '%저항%'
# 'ilike'는 PostgreSQL 전용. SQLite에서는 like()와 동일하게 동작.
```

### getattr 동적 정렬
```python
# sort_by = "price" 라는 문자열을 Product.price 컬럼 객체로 변환
column = getattr(Product, sort_by, None)
# → Product.price 와 동일

# None이면 잘못된 컬럼명 — 정렬 생략
if column is not None:
    query = query.order_by(column.desc())
```

### count() — 필터 적용 후 전체 건수
```python
# 반드시 offset/limit 적용 전에 호출해야 정확한 총 건수를 얻음
total = query.count()          # 필터 후 전체 건수
items = query.offset(offset).limit(size).all()  # 페이지 데이터
```

---

## 사전 세팅 — 테스트 데이터 입력

서버 실행:
```bash
uvicorn day4.main:app --reload
```

### 카테고리 2개 생성
```bash
curl -s -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "전자부품", "description": "저항, 콘덴서 등"}' | python -m json.tool

curl -s -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "공구", "description": "납땜 도구 등"}' | python -m json.tool
```

### 상품 10개 생성 (category_id 1: 전자부품, 2: 공구)
```bash
curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "저항 100Ω", "price": 50, "stock": 200, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "저항 220Ω", "price": 50, "stock": 150, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "저항 1kΩ", "price": 60, "stock": 100, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "콘덴서 10μF", "price": 120, "stock": 80, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "콘덴서 100μF", "price": 200, "stock": 60, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "LED 빨강", "price": 80, "stock": 500, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "LED 파랑", "price": 80, "stock": 500, "category_id": 1}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "인두기 30W", "price": 15000, "stock": 10, "category_id": 2}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "납땜 와이어 0.8mm", "price": 3500, "stock": 30, "category_id": 2}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "브레드보드", "price": 2500, "stock": 25, "category_id": 2}' | python -m json.tool
```

### 주문 2건 생성
```bash
curl -s -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "홍길동",
    "items": [
      {"product_id": 1, "quantity": 10},
      {"product_id": 4, "quantity": 2}
    ]
  }' | python -m json.tool

curl -s -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "김철수",
    "items": [
      {"product_id": 8, "quantity": 1},
      {"product_id": 10, "quantity": 3}
    ]
  }' | python -m json.tool
```

---

## TODO 해설

### TODO 27 ★★☆ — PaginatedResponse 스키마

`schemas.py`에 정의된 제네릭 페이지네이션 응답 스키마입니다.

```python
class PaginatedResponse(BaseModel):
    total: int   # 필터 적용 후 전체 건수
    page: int    # 현재 페이지
    size: int    # 페이지당 건수
    items: list  # 실제 데이터 목록
```

응답 예시:
```json
{
  "total": 10,
  "page": 1,
  "size": 5,
  "items": [...]
}
```

### TODO 28 ★☆☆ — ProductSearchParams 없이 Query 파라미터 직접 사용

별도 스키마 클래스를 만드는 대신 FastAPI `Query()`를 함수 파라미터에 직접 선언합니다.
검색 조건이 단순할 때 더 간결하고, Swagger UI에서도 자동으로 문서화됩니다.

```python
def list_products(
    search: str | None = Query(default=None),
    ...
):
```

### TODO 29 ★★☆ — offset/limit 페이지네이션

```python
page: int = Query(default=1, ge=1)
size: int = Query(default=10, ge=1, le=100)

total = query.count()          # 1. 전체 건수 (offset 전에!)
offset = (page - 1) * size     # 2. 건너뛸 행 수 계산
items = query.offset(offset).limit(size).all()  # 3. 페이지 데이터
```

**실수 방지**: `count()`를 `offset().limit()` 이후에 호출하면 페이지 크기만큼만 집계됩니다.
반드시 페이지네이션 적용 전에 호출하세요.

### TODO 30 ★★☆ — ilike 이름 검색

```python
if search:
    query = query.filter(Product.name.ilike(f"%{search}%"))
```

`ilike`는 PostgreSQL의 대소문자 무관 LIKE입니다.
`%저항%` → "저항 100Ω", "저항 220Ω" 모두 매칭됩니다.

### TODO 31 ★★☆ — 가격 범위 필터

```python
if min_price is not None:
    query = query.filter(Product.price >= min_price)
if max_price is not None:
    query = query.filter(Product.price <= max_price)
```

`0`도 유효한 값이므로 `if min_price:` 대신 `if min_price is not None:`을 사용합니다.

### TODO 32 ★★★ — 동적 정렬

```python
sort_by: str = Query(default="id")
order: str = Query(default="asc")

column = getattr(Product, sort_by, None)
# getattr(객체, 속성명, 기본값) — 속성이 없으면 None 반환
if column is not None:
    if order == "desc":
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())
```

잘못된 컬럼명(예: `sort_by="이름`)이 들어와도 `getattr`의 세 번째 인자 `None` 덕분에
오류 없이 정렬을 생략합니다.

### TODO 33 ★★☆ — 주문 목록 페이지네이션 + status 필터

`orders.py`의 `list_orders`에 페이지네이션과 상태 필터를 추가합니다.

```python
status: str | None = Query(default=None)

if status:
    query = query.filter(Order.status == status)
```

### TODO 34 ★★★ — 통합 API

TODO 29~32를 하나의 `list_products`에 모두 합치는 과제입니다.
`products.py`의 `list_products` 함수가 이미 완성된 통합 구현을 보여줍니다.
각 TODO 블록 주석을 읽으면서 어떻게 쌓였는지 확인하세요.

---

## 검증 체크리스트

서버 실행 후 아래를 순서대로 확인하세요.

### 1. 기본 페이지네이션
```bash
# 5개씩 1페이지
curl -s "http://localhost:8000/products/?page=1&size=5" | python -m json.tool
# → total=10, page=1, size=5, items 5개

# 5개씩 2페이지
curl -s "http://localhost:8000/products/?page=2&size=5" | python -m json.tool
# → total=10, page=2, size=5, items 5개
```

### 2. 이름 부분검색
```bash
curl -s "http://localhost:8000/products/?search=저항" | python -m json.tool
# → total=3, items에 저항 100Ω / 220Ω / 1kΩ

curl -s "http://localhost:8000/products/?search=led" | python -m json.tool
# → ilike 덕분에 대소문자 무관, total=2
```

### 3. 가격 범위 필터
```bash
curl -s "http://localhost:8000/products/?min_price=100&max_price=500" | python -m json.tool
# → 100~500원 상품만 반환

curl -s "http://localhost:8000/products/?min_price=1000" | python -m json.tool
# → 1000원 이상 상품만 반환
```

### 4. 동적 정렬
```bash
# 가격 내림차순
curl -s "http://localhost:8000/products/?sort_by=price&order=desc" | python -m json.tool
# → items[0].price 가 가장 높아야 함

# 이름 오름차순
curl -s "http://localhost:8000/products/?sort_by=name&order=asc" | python -m json.tool
```

### 5. 복합 조건
```bash
# 전자부품 카테고리에서 가격 오름차순, 2페이지
curl -s "http://localhost:8000/products/?category_id=1&sort_by=price&order=asc&page=2&size=3" | python -m json.tool
```

### 6. 주문 목록 페이지네이션 + status 필터
```bash
curl -s "http://localhost:8000/orders/?page=1&size=5" | python -m json.tool
# → total, page, size, items 구조 확인

curl -s "http://localhost:8000/orders/?status=pending" | python -m json.tool
# → pending 상태 주문만 반환
```

### 7. 응답 구조 확인
모든 목록 API 응답이 아래 형태여야 합니다:
```json
{
  "total": 10,
  "page": 1,
  "size": 5,
  "items": [...]
}
```

---

## 다음: Day 5 — Alembic 마이그레이션

- `alembic init` 으로 마이그레이션 환경 초기화
- `alembic revision --autogenerate` 로 스키마 변경 자동 감지
- `alembic upgrade head` 로 마이그레이션 적용
- 컬럼 추가/삭제/이름 변경을 코드로 관리하는 방법
