# Day 7 — MES 작업지시 + 상태머신 워크북

## 핵심 개념

### 상태 머신 (State Machine)

WorkOrder의 `status`는 아무 값이나 가질 수 없습니다.
허용된 순서대로만 전이해야 하며, 이를 **상태 머신**이라고 합니다.

**상태 전이 다이어그램**

```
              start()
┌─────────┐  ──────────>  ┌──────────────┐
│ PENDING │               │ IN_PROGRESS  │
└────┬────┘               └──┬────────┬──┘
     │                       │        │
     │ cancel()    complete() │        │ cancel()
     │                       v        │
     │               ┌───────────┐    │
     │               │ COMPLETED │    │
     │               └───────────┘    │
     │                                │
     └──────────────────────>─────────┘
                       ┌───────────┐
                       │ CANCELLED │
                       └───────────┘
```

**허용 전이 목록**

| 현재 상태   | 전이 가능한 상태             |
|-------------|------------------------------|
| PENDING     | IN_PROGRESS, CANCELLED       |
| IN_PROGRESS | COMPLETED, CANCELLED         |
| COMPLETED   | (없음 — 완료는 되돌릴 수 없음) |
| CANCELLED   | (없음 — 취소는 되돌릴 수 없음) |

**금지 전이 목록**

| 시도        | 이유                                    |
|-------------|-----------------------------------------|
| PENDING → COMPLETED  | 시작 없이 완료 불가               |
| COMPLETED → PENDING  | 완료된 작업 되돌리기 불가         |
| CANCELLED → IN_PROGRESS | 취소 후 재개 불가              |
| IN_PROGRESS → PENDING | 진행 중 대기 상태 복귀 불가      |

---

### BOM 연동 자재 소요량 계산

작업지시 생성 시 BOM에서 자동으로 소요자재를 계산합니다.

```
WorkOrderItem.required_qty = BOMEntry.quantity × WorkOrder.quantity
```

예: BOM에 `자재A: 2개/완제품` 이 등록되어 있고, 작업지시 수량이 50개라면
→ `WorkOrderItem.required_qty = 2 × 50 = 100`

---

### 복합 트랜잭션

작업 시작(`start`) 시 여러 자재의 재고를 한 번에 차감합니다.
하나라도 재고 부족이면 **전체 롤백** — 일부만 차감된 채 남으면 안 됩니다.

```python
try:
    for item in work_order.items:
        if material.stock < item.required_qty:
            raise HTTPException(400, "재고 부족")
        material.stock -= item.required_qty
    db.commit()
except HTTPException:
    db.rollback()
    raise
```

---

## 사전 세팅 curl

아래 명령을 순서대로 실행하면 테스트 데이터가 준비됩니다.

```bash
# 1. 카테고리 생성 — 완제품용
curl -s -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "완제품", "description": "조립 완성품"}' | python -m json.tool

# 2. 카테고리 생성 — 원자재용
curl -s -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "원자재", "description": "부품 및 원재료"}' | python -m json.tool

# 3. 완제품 등록 (category_id=1)
curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "스마트폰 케이스", "price": 15000, "stock": 0, "category_id": 1}' | python -m json.tool

# 4. 자재 3종 등록 (category_id=2)
curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "플라스틱 외장재", "price": 2000, "stock": 500, "category_id": 2}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "강화유리", "price": 3000, "stock": 300, "category_id": 2}' | python -m json.tool

curl -s -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "접착제", "price": 500, "stock": 1000, "category_id": 2}' | python -m json.tool

# 5. 공정 등록
curl -s -X POST http://localhost:8000/processes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "케이스 조립 공정", "description": "부품 조립 후 검사"}' | python -m json.tool

# 6. BOM 등록 — 완제품(id=1) 1개 기준 소요 자재
# 플라스틱 외장재 1개
curl -s -X POST http://localhost:8000/bom/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "material_id": 2, "quantity": 1}' | python -m json.tool

# 강화유리 1개
curl -s -X POST http://localhost:8000/bom/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "material_id": 3, "quantity": 1}' | python -m json.tool

# 접착제 0.5개(단위)
curl -s -X POST http://localhost:8000/bom/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "material_id": 4, "quantity": 0.5}' | python -m json.tool

# 7. 작업지시 생성 — 스마트폰 케이스 100개 생산
curl -s -X POST http://localhost:8000/work-orders/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "process_id": 1, "quantity": 100}' | python -m json.tool

# 8. 작업 시작 (work_order_id=1)
curl -s -X PATCH http://localhost:8000/work-orders/1/start | python -m json.tool

# 9. 작업 완료
curl -s -X PATCH http://localhost:8000/work-orders/1/complete | python -m json.tool

# 10. 대시보드 확인
curl -s http://localhost:8000/work-orders/dashboard | python -m json.tool
```

---

## TODO 해설

### TODO 54 — WorkOrder 모델 (★★☆)

`order_number`는 `unique=True`로 선언합니다. 작업지시 번호는 시스템 전체에서
중복되면 안 되기 때문입니다. `started_at`, `completed_at`은 `nullable=True` —
아직 시작/완료 전에는 값이 없어야 합니다.

### TODO 55 — WorkOrderItem 모델 (★★☆)

`required_qty`와 `consumed_qty`를 `Float`으로 선언하는 이유:
자재는 0.5kg, 2.5L처럼 소수점 단위로 소요될 수 있기 때문입니다.

### TODO 56 — WorkOrder relationships (★☆☆)

`WorkOrder.product`는 `foreign_keys=[product_id]`를 명시합니다.
`Product` 테이블을 참조하는 FK가 여러 개는 아니지만, `WorkOrderItem.material`도
같은 `Product` 테이블을 참조하므로 SQLAlchemy가 혼동하지 않도록 명시하는 습관을 들이세요.

### TODO 57 — WorkOrderCreate 스키마 (★★☆)

`order_number`를 Create 스키마에 포함하지 않는 것이 핵심입니다.
서버가 자동 생성하는 값을 클라이언트가 임의로 지정하면 충돌 위험이 있습니다.

### TODO 58 — WorkOrderItemResponse + WorkOrderResponse (★★☆)

`WorkOrderItemResponse`에 `material_name`(str)을 포함시키는 이유:
프론트엔드에서 material_id만 받으면 자재 이름을 표시하려고 추가 API를 호출해야 합니다.
응답에 이름을 포함시켜 불필요한 추가 요청을 줄입니다.

단, Pydantic `from_attributes=True`는 ORM 속성을 자동 직렬화하지만,
`material_name`은 모델에 없는 계산 필드입니다. `_build_work_order_response()`
헬퍼 함수에서 `item.material.name`을 명시적으로 꺼내는 방식으로 해결합니다.

### TODO 59 — 작업지시 생성 (★★★)

`db.flush()` 후 WorkOrderItem을 생성하는 이유:
`flush`는 commit 없이 DB에 INSERT해서 `work_order.id`(PK)를 확보합니다.
이후 `WorkOrderItem.work_order_id = work_order.id`를 설정할 수 있습니다.

### TODO 60 — 작업지시 목록 (★★☆)

`status.upper()`로 대소문자 무관하게 필터링할 수 있게 합니다.
`GET /work-orders?status=pending`도 `GET /work-orders?status=PENDING`과 동일하게 동작합니다.

### TODO 61 — 작업 시작 (★★★)

재고 부족 검사를 차감 전에 먼저 합니다.
"차감하다가 중간에 실패"하는 상황을 방지하기 위해
모든 자재의 재고를 확인한 후 일괄 차감하는 것이 더 안전합니다.

### TODO 62 — 작업 완료 (★★★)

완제품 재고 증가는 `COMPLETED` 전이 시에만 발생합니다.
`CANCELLED`로 전이하면 완제품 재고는 증가하지 않습니다.

### TODO 63 — 작업 취소 (★★★)

현재 상태에 따라 분기 처리합니다:
- `PENDING` → 취소: 재고 변동 없음 (아직 자재를 꺼내지 않음)
- `IN_PROGRESS` → 취소: 이미 차감한 자재 재고를 원복

### TODO 64 — 실적 등록 (★★★) 보너스

`consumed_qty > required_qty` 초과 방지.
실제 현장에서는 스크랩(불량) 때문에 필요량보다 더 소비하기도 하지만,
이 워크북에서는 단순화를 위해 초과를 금지합니다.

### TODO 65 — 대시보드 (★★★) 보너스

`func.group_by()`와 `func.coalesce()`를 활용합니다.
`coalesce(sum(...), 0)`은 결과가 NULL(행이 없을 때)인 경우 0으로 대체합니다.

---

## 검증 체크리스트

- [ ] `POST /work-orders/` → BOM이 없는 완제품으로 생성 시 items가 빈 배열인지 확인
- [ ] `PATCH /work-orders/1/start` → 자재 재고 부족 시 400 응답 + 재고 미차감 확인
- [ ] `PATCH /work-orders/1/start` → 이미 IN_PROGRESS 상태에서 다시 start 시 400 확인
- [ ] `PATCH /work-orders/1/cancel` (IN_PROGRESS 상태) → 자재 재고 원복 확인
- [ ] `GET /work-orders/dashboard` → 상태별 건수 집계 정확성 확인

---

## 더 나아가기: 실무 MES에서 추가로 다루는 테이블

1. **설비(Equipment)**: 어떤 기계로 작업하는지. WorkOrder에 `equipment_id` FK
2. **품질검사(QualityCheck)**: 완료된 작업의 양품/불량 수량
3. **Lot 관리(Lot)**: 자재/제품 입고 단위 추적. FIFO 재고 관리
4. **생산계획(ProductionPlan)**: 월/주 단위 생산 목표

이 테이블들을 추가하는 것을 Day 8 이후 자율 과제로 도전해보세요!
