# Day 3 / complete — 주문 시스템 + 트랜잭션 완성 참고

## 학습 목표
한 요청에서 여러 테이블을 동시에 변경할 때 **원자성**을 보장하는 패턴을 익힌다.

## DB 구조

```
categories ─< products ─< order_items >─ orders
```

## 핵심 4가지

| 패턴 | 어디 | 왜 필요한가 |
|------|------|-------------|
| `db.flush()` | `routes/orders.py:create_order` | commit 없이 PK(`order.id`) 즉시 확보 |
| `try/except HTTPException` | 모든 트랜잭션 | 의도된 에러는 그대로 클라이언트에 전달 |
| `db.rollback()` | 모든 except | 부분 변경 방지, 원자성 보장 |
| 단가 스냅샷 (`unit_price`) | `OrderItem` | 상품가 변동 후에도 과거 주문 무결성 유지 |

## 실행

```bash
docker compose down -v && docker compose up -d
uvicorn day3.complete.main:app --reload
```

## 검증 curl

```bash
# 1) 카테고리/상품 준비
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" \
  -d '{"name": "전자제품"}'
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" \
  -d '{"name": "마우스", "price": 25000, "stock": 10, "category_id": 1}'
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" \
  -d '{"name": "키보드", "price": 89000, "stock": 5, "category_id": 1}'

# 2) 주문 생성
curl -X POST http://localhost:8000/orders/ -H "Content-Type: application/json" \
  -d '{"customer_name": "홍길동", "items": [{"product_id":1,"quantity":2},{"product_id":2,"quantity":1}]}'
# 기대: total_amount = 25000*2 + 89000 = 139000

# 3) 재고 부족 → 400 + 재고 변동 없음
curl -X POST http://localhost:8000/orders/ -H "Content-Type: application/json" \
  -d '{"customer_name": "테스터", "items": [{"product_id":1,"quantity":999}]}'

# 4) 주문 취소 → 재고 원복
curl -X DELETE http://localhost:8000/orders/1/cancel
curl http://localhost:8000/products/1
# 기대: stock 이 주문 전 수량으로 복구됨
```
