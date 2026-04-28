# Day 3 / practice — Booking 좌석 예약 트랜잭션 변형 문제

> `day3/complete/routes/orders.py` 의 `create_order` 를 띄워두고 풀어보세요.
> 트랜잭션 패턴은 똑같고, 단어만 다릅니다.

## 변형 매핑표

| complete | practice |
|----------|----------|
| Order | Booking |
| OrderItem | BookingSeat |
| `quantity` | `seat_count` |
| `unit_price` | `seat_price` |
| `total_amount` | `total_price` |
| 재고 차감 | 좌석 차감 (의미 변경) |
| Product/category | Item/brand (Day 2 practice 동일) |

## TODO 10개

| # | 파일 | 내용 |
|---|------|------|
| 1 | `models.py` | `Booking` 모델 정의 |
| 2 | `models.py` | `BookingSeat` 모델 정의 (FK 2개) |
| 3 | `schemas.py` | `BookingSeatCreate` |
| 4 | `schemas.py` | `BookingCreate` (nested seats list) |
| 5 | `schemas.py` | `BookingSeatResponse` (`from_attributes=True` 필수) |
| 6 | `schemas.py` | `BookingResponse` (nested `seats: list[...]`) |
| 7 | `routes/bookings.py` | POST 예약 생성 + flush/rollback |
| 8 | `routes/bookings.py` | GET 목록 |
| 9 | `routes/bookings.py` | GET 단건 |
| 10 | `routes/bookings.py` | DELETE 예약 취소 + 좌석 원복 |

## 환경 세팅

```bash
docker compose down -v && docker compose up -d
uvicorn day3.practice.main:app --reload
```

## 검증 체크리스트

```bash
# 1) 브랜드/Item 준비 (Item 의 stock 이 좌석 잔여수)
curl -X POST http://localhost:8000/brands/ -H "Content-Type: application/json" \
  -d '{"name": "공연장A"}'
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" \
  -d '{"name": "VIP석", "price": 50000, "stock": 10, "brand_id": 1}'

# 2) 예약 생성 — 5좌석
curl -X POST http://localhost:8000/bookings/ -H "Content-Type: application/json" \
  -d '{"customer_name": "홍길동", "seats": [{"item_id":1,"seat_count":5}]}'
# 기대: total_price = 50000 * 5 = 250000

# 3) 좌석 부족 → 400 + 좌석 변동 없음 (rollback 검증)
curl -X POST http://localhost:8000/bookings/ -H "Content-Type: application/json" \
  -d '{"customer_name": "테스터", "seats": [{"item_id":1,"seat_count":999}]}'

# 4) nested 응답 확인
curl http://localhost:8000/bookings/1
# 기대: seats 배열에 item_id, seat_count, seat_price 포함

# 5) 취소 + 좌석 원복
curl -X DELETE http://localhost:8000/bookings/1/cancel
curl http://localhost:8000/items/1
# 기대: stock 이 차감 전(10)으로 복구

# 6) 이중 취소 방지
curl -X DELETE http://localhost:8000/bookings/1/cancel
# 기대: 400 "이미 취소된 예약입니다"
```

## 학습 포인트

### 1. flush vs commit
- `db.flush()` 후엔 PK 사용 가능, 하지만 commit 전이라 rollback 가능.
- `db.commit()` 후엔 영구 반영.

### 2. rollback 누락 함정
```python
try:
    db.add(booking); db.flush()
    raise HTTPException(400, "재고부족")
except HTTPException:
    raise   # ← rollback 누락! 세션이 dirty 상태로 남음
```
이후 같은 세션에서 다른 요청이 오면 모두 실패한다. 반드시 `db.rollback()` 후 `raise`.

### 3. nested from_attributes
`BookingResponse.seats: list[BookingSeatResponse]` 변환은 양쪽 스키마 모두에 `from_attributes=True` 가 있어야 동작.

## 막혔을 때
- TODO 1~2 모델 → `day3/complete/models.py` Order/OrderItem 통째로
- TODO 7 트랜잭션 → `day3/complete/routes/orders.py:create_order` 줄단위 비교
