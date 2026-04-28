# Day 6 / complete — 자기참조 공정 + BOM(Dual FK) 완성 참고

## 학습 포인트 두 가지

### 1. 자기참조 FK (Process)
같은 테이블의 다른 행을 가리킨다. 트리/계층 표현.

```
processes
┌─────┬──────────────┬────────────┐
│ id  │ name         │ parent_id  │
├─────┼──────────────┼────────────┤
│  1  │ SMT 실장     │   NULL     │  ← 최상위
│  2  │ 부품 배치    │     1      │
│  3  │ 납땜         │     1      │
│  4  │ 검사         │   NULL     │  ← 최상위
└─────┴──────────────┴────────────┘
```

핵심 코드:
```python
parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)
parent = relationship("Process", remote_side="Process.id", back_populates="children")
children = relationship("Process", back_populates="parent")
```

`remote_side` 가 없으면 SQLAlchemy 가 어느 쪽이 부모인지 못 정해 에러.

### 2. Dual FK (BOMEntry)
같은 테이블을 두 번 참조. `foreign_keys=[col]` 명시 필수.

```python
product_id  = Column(Integer, ForeignKey("products.id"))
material_id = Column(Integer, ForeignKey("products.id"))
product  = relationship("Product", foreign_keys=[product_id])
material = relationship("Product", foreign_keys=[material_id])
```

## 검증 curl

```bash
docker compose down -v && docker compose up -d
uvicorn day6.complete.main:app --reload

# 카테고리 + 완제품 + 자재 등록
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" -d '{"name":"완제품"}'
curl -X POST http://localhost:8000/categories/ -H "Content-Type: application/json" -d '{"name":"자재"}'
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" -d '{"name":"PCB","price":15000,"stock":10,"category_id":1}'
curl -X POST http://localhost:8000/products/ -H "Content-Type: application/json" -d '{"name":"저항","price":50,"stock":1000,"category_id":2}'

# 최상위 공정
curl -X POST http://localhost:8000/processes/ -H "Content-Type: application/json" -d '{"name":"SMT"}'
# 하위 공정
curl -X POST http://localhost:8000/processes/ -H "Content-Type: application/json" -d '{"name":"부품 배치","parent_id":1}'
# 최상위만 조회
curl http://localhost:8000/processes/

# BOM 등록 + 비용 집계
curl -X POST http://localhost:8000/bom/ -H "Content-Type: application/json" -d '{"product_id":1,"material_id":2,"quantity":10}'
curl http://localhost:8000/bom/product/1/cost
```
