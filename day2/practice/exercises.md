# Day 2 / practice — Brand 1:N Item 변형 문제

> 옆 폴더 `day2/complete/` 의 Category-Product 코드를 띄워두고 풀어보세요.
> 같은 1:N 패턴, 이름만 다른 도메인입니다.

## 변형 매핑표

| complete | practice |
|----------|----------|
| Category | Brand |
| Product | Item |
| `categories.id` | `brands.id` |
| `category_id` (FK) | `brand_id` (FK) |
| `Category.products` (relationship) | `Brand.items` |
| `Product.category` (relationship) | `Item.brand` |

## TODO 10개

| # | 파일 | 내용 | 난이도 |
|---|------|------|--------|
| 1 | `models.py` | `Brand.items = relationship(...)` 추가 | ★☆☆ |
| 2 | `models.py` | `Item.brand_id` ForeignKey 컬럼 | ★★☆ |
| 3 | `models.py` | `Item.brand = relationship(...)` 추가 | ★★☆ |
| 4 | `schemas.py` | `ItemCreate` 5개 필드 정의 | ★☆☆ |
| 5 | `schemas.py` | `ItemResponse` 8개 필드 + `model_config` | ★☆☆ |
| 6 | `routes/items.py` | POST 생성 + FK 검증 | ★★☆ |
| 7 | `routes/items.py` | GET 목록 + brand_id 필터 | ★★☆ |
| 8 | `routes/items.py` | GET 단건 | ★☆☆ |
| 9 | `routes/items.py` | PUT 수정 + FK 검증 | ★★★ |
| 10 | `routes/items.py` | DELETE | ★☆☆ |

## 환경 세팅

```bash
docker compose down -v && docker compose up -d
uvicorn day2.practice.main:app --reload
```

## 검증 체크리스트

```bash
# 1) 브랜드 생성
curl -X POST http://localhost:8000/brands/ -H "Content-Type: application/json" \
  -d '{"name": "삼성", "description": "전자기기 브랜드"}'

# 2) 상품 생성 (brand_id=1)
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
  -d '{"name": "갤럭시", "price": 1200000, "stock": 50, "brand_id": 1}'

# 3) 존재하지 않는 brand_id → 404
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
  -d '{"name": "오류", "price": 1000, "brand_id": 9999}'
# 기대: {"detail":"브랜드를 찾을 수 없습니다"}

# 4) 브랜드별 필터
curl "http://localhost:8000/items/?brand_id=1"

# 5) 수정
curl -X PUT http://localhost:8000/items/1 -H "Content-Type: application/json" \
  -d '{"name": "갤럭시 S", "price": 1300000, "stock": 40, "brand_id": 1}'
```

## 막혔을 때
- TODO 1, 3 (relationship) → `day2/complete/models.py` 의 `Category.products` / `Product.category`
- TODO 2 (ForeignKey) → `day2/complete/models.py` 의 `category_id` 라인
- TODO 6, 9 (FK 검증) → `day2/complete/routes/products.py` 의 create_product Step 1, update_product 후반부
- back_populates 가 문제일 때 → 양쪽 이름이 1글자라도 다르면 침묵하다 런타임에 깨진다는 함정
