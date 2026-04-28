# Day 7 / complete — 상태머신 + BOM 자재 차감 완성 참고

## 학습 목표
1. 상태 전이를 데이터(`ALLOWED_TRANSITIONS` dict) 로 표현
2. BOM 으로부터 작업지시 자동 생성 (quantity 곱셈)
3. 시작 시 일괄 검증 후 일괄 차감 (트랜잭션 원자성)
4. 취소 시 진행 단계에 따라 분기 (PENDING/IN_PROGRESS)
5. `func.count`, `func.sum`, `func.coalesce` 집계

## 상태 전이도

```
              start()
PENDING   ─────────────▶  IN_PROGRESS
   │ cancel()                │ complete()
   ▼                          ▼
CANCELED                   COMPLETED
                              ▲
                              │ cancel()
                          IN_PROGRESS (도 cancel 가능, 자재 원복)
```

## 검증 curl

```bash
docker compose down -v && docker compose up -d
uvicorn day7.complete.main:app --reload

# 데이터 준비
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" -d '{"name":"완제품"}'
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" -d '{"name":"자재"}'
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" -d '{"name":"PCB","price":15000,"stock":0,"category_id":1}'
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" -d '{"name":"저항","price":50,"stock":1000,"category_id":2}'
curl -X POST http://localhost:8000/processes/ -H "Content-Type: application/json" -d '{"name":"SMT"}'
curl -X POST http://localhost:8000/bom/ -H "Content-Type: application/json" -d '{"product_id":1,"material_id":2,"quantity":10}'

# 작업지시 생성 (PCB 50개)
curl -X POST http://localhost:8000/work-orders/ -H "Content-Type: application/json" -d '{"product_id":1,"process_id":1,"quantity":50}'
# 기대: items 에 자재 required_qty=500 (10*50)

# 시작 → 자재 차감
curl -X PATCH http://localhost:8000/work-orders/1/start
curl http://localhost:8000/products/2   # 자재 재고 1000→500 확인

# 완료 → 완제품 재고 +50
curl -X PATCH http://localhost:8000/work-orders/1/complete
curl http://localhost:8000/products/1   # PCB 0→50

# 대시보드 (집계)
curl http://localhost:8000/work-orders/dashboard
# 기대: by_status: [{COMPLETED:1}], total_produced: 50

# 잘못된 전이 → 400
curl -X PATCH http://localhost:8000/work-orders/1/start
# 기대: 400 "COMPLETED → IN_PROGRESS 전이는 허용되지 않습니다"
```
