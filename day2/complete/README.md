# Day 2 / complete — Category 1:N Product 완성 참고

## 학습 목표
외래키(ForeignKey) + relationship 양방향 연결을 코드로 보고 이해한다.

## DB 구조

```
┌────────────┐         ┌────────────────────────┐
│ categories │ 1     N │ products               │
│────────────│ ───────▶│────────────────────────│
│ id (PK)    │         │ id (PK)                │
│ name       │         │ name                   │
│ ...        │         │ price                  │
└────────────┘         │ stock                  │
                       │ category_id (FK) ──────┘
                       │ ...
                       └────────────────────────┘
```

## 엔드포인트
- `/categories/*` — Day 1 동일
- `/products/*` — POST/GET/PUT 에 **FK 사전 검증** 추가

## 실행

```bash
docker compose up -d
uvicorn day2.complete.main:app --reload
# http://localhost:8000/docs
```

## 검증 curl

```bash
# 1) 카테고리 생성
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" \
  -d '{"name": "전자제품"}'

# 2) 상품 생성 (category_id=1)
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" \
  -d '{"name": "마우스", "price": 25000, "stock": 10, "category_id": 1}'

# 3) 존재하지 않는 카테고리 → 404
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" \
  -d '{"name": "오류상품", "price": 1000, "category_id": 9999}'
# 기대: {"detail":"카테고리를 찾을 수 없습니다"}

# 4) 카테고리별 필터
curl "http://localhost:8000/products/?category_id=1"
```

## 핵심 라인 인덱스

| 학습 포인트 | 파일 | 내용 |
|-----------|------|------|
| FK 정의 SQL 매핑 | models.py | `category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)` |
| 양방향 relationship | models.py | `Category.products` ↔ `Product.category` (back_populates 짝) |
| FK 사전 검증 패턴 | routes/products.py | create_product 의 Step 1 |
| onupdate 자동 갱신 | models.py | `updated_at` 컬럼 |
