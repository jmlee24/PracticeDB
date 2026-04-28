# Day 7 / practice — Shipment 상태머신 (HOLD 상태 추가) 변형

## 매핑

| complete (WorkOrder) | practice (Shipment) |
|----------|----------|
| `WorkOrder` | `Shipment` |
| `WorkOrderItem` | `ShipmentItem` |
| `process_id` | `department_id` |
| `started_at`/`completed_at` | `shipped_at`/`delivered_at` |
| `consumed_qty` | `actual_qty` |
| 4개 상태 | **5개 상태 (HOLD 추가)** |
| `start/complete/cancel` | `ship/deliver/hold/resume/cancel` |

## ★ 핵심 차이: 5개 상태 머신

```
              ship                     deliver
  PENDING ──────────▶ SHIPPING ─────────▶ DELIVERED
     │                   │ return
     │ hold              │
     ▼                    ▼
   HOLD ──resume──▶ PENDING       RETURNED
     │ cancel
     ▼
   CANCELED
```

`ALLOWED_TRANSITIONS` 키 6개 (complete 는 4개), 각 키의 다음 상태 목록도 다르다.

## TODO 14개

| # | 파일 | 내용 |
|---|------|------|
| 1 | `models.py` | Shipment 모델 |
| 2 | `models.py` | ShipmentItem 모델 |
| 3 | `schemas.py` | ShipmentCreate |
| 4 | `schemas.py` | ShipmentItemResponse |
| 5 | `schemas.py` | ShipmentResponse (nested items) |
| 6 | `routes/shipments.py` | ALLOWED_TRANSITIONS dict (HOLD 추가) |
| 7 | `routes/shipments.py` | `_check_transition` 헬퍼 |
| 8 | `routes/shipments.py` | POST 생성 (Recipe → ShipmentItem 자동) |
| 9 | `routes/shipments.py` | PATCH ship (자재 차감) |
| 10 | `routes/shipments.py` | PATCH hold (신규!) |
| 11 | `routes/shipments.py` | PATCH resume (신규!) |
| 12 | `routes/shipments.py` | PATCH deliver |
| 13 | `routes/shipments.py` | PATCH cancel (조건부 자재 원복) |
| 14 | `routes/shipments.py` | GET 목록 |

## 환경 세팅

```bash
docker compose down -v && docker compose up -d
uvicorn day7.practice.main:app --reload
```

## 검증

```bash
# 데이터 준비
curl -X POST http://localhost:8000/brands/ -H "Content-Type: application/json" -d '{"name":"제조사"}'
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" -d '{"name":"완제품","price":10000,"stock":0,"brand_id":1}'
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" -d '{"name":"부품","price":1000,"stock":1000,"brand_id":1}'
curl -X POST http://localhost:8000/departments/ -H "Content-Type: application/json" -d '{"name":"물류팀"}'
curl -X POST http://localhost:8000/recipes/ -H "Content-Type: application/json" -d '{"product_id":1,"material_id":2,"quantity":5}'

# 출고지시 생성 (완제품 10개)
curl -X POST http://localhost:8000/shipments/ -H "Content-Type: application/json" -d '{"product_id":1,"department_id":1,"quantity":10}'
# 기대: items.required_qty = 50 (5*10)

# HOLD 시연 (신규!)
curl -X PATCH http://localhost:8000/shipments/1/hold
# 기대: status="HOLD"

# resume → PENDING (신규!)
curl -X PATCH http://localhost:8000/shipments/1/resume
# 기대: status="PENDING"

# 출고 시작 (자재 차감)
curl -X PATCH http://localhost:8000/shipments/1/ship
curl http://localhost:8000/items/2   # 재고 1000→950 확인

# 잘못된 전이 → 400
curl -X PATCH http://localhost:8000/shipments/1/hold
# 기대: 400 "SHIPPING → HOLD 전이는 허용되지 않습니다"

# 배송 완료
curl -X PATCH http://localhost:8000/shipments/1/deliver

# 취소 시 PENDING/HOLD 면 자재 변동 없음, SHIPPING 이었다면 원복
```

## 함정 / 학습 포인트

1. **새 상태 키 누락**: `ALLOWED_TRANSITIONS` 에 `"HOLD"` 자체를 키로 추가해야 한다. 다른 상태에서 HOLD 로 가는 것만 추가하고 끝나면 HOLD 에서 어딘가로 갈 때 KeyError 발생.

2. **`.get(current, [])`** 패턴: complete 와 동일하게 안전 조회 (있으면 리스트, 없으면 빈 리스트).

3. **취소 시 분기**:
   - `PENDING/HOLD` 에서 취소: 자재 차감 전이라 원복 불필요
   - `SHIPPING` 에서 취소: 차감했던 자재 원복
