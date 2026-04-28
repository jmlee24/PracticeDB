# Day 6 / practice — Department 트리 + Recipe Dual FK 변형

## 매핑

| complete | practice |
|----------|----------|
| `Process` (자기참조) | `Department` (자기참조) |
| `BOMEntry` (dual FK to Product) | `Recipe` (dual FK to Item) |
| `processes.parent_id` | `departments.parent_id` |
| `BOMEntry.product_id/material_id` → products | `Recipe.product_id/material_id` → items |

## TODO 12개

| # | 파일 | 내용 |
|---|------|------|
| 1 | `models.py` | `Department` 자기참조 FK + parent/children relationship |
| 2 | `models.py` | `Recipe` dual FK + `foreign_keys=[col]` 명시 |
| 3 | `schemas.py` | `DepartmentCreate` |
| 4 | `schemas.py` | `DepartmentResponse` |
| 5 | `schemas.py` | `RecipeCreate` |
| 6 | `schemas.py` | `RecipeResponse` (계산 필드 `material_name` 포함) |
| 7 | `routes/departments.py` | POST 생성 + parent 검증 |
| 8 | `routes/departments.py` | GET 목록 (`parent_id is None` 으로 최상위) |
| 9 | `routes/departments.py` | GET 단건 |
| 10 | `routes/recipes.py` | POST 생성 + 두 Item 검증 + 동일 ID 금지 |
| 11 | `routes/recipes.py` | GET 제품별 Recipe 목록 |
| 12 | `routes/recipes.py` | GET 자재 비용 집계 |

## 환경 세팅

```bash
docker compose down -v && docker compose up -d
uvicorn day6.practice.main:app --reload
```

## 검증

```bash
curl -X POST http://localhost:8000/brands/ -H "Content-Type: application/json" -d '{"name":"제품"}'
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" -d '{"name":"케이크","price":10000,"stock":10,"brand_id":1}'
curl -X POST http://localhost:8000/items/ -H "Content-Type: application/json" -d '{"name":"밀가루","price":2000,"stock":1000,"brand_id":1}'

# 부서 트리
curl -X POST http://localhost:8000/departments/ -H "Content-Type: application/json" -d '{"name":"본사"}'
curl -X POST http://localhost:8000/departments/ -H "Content-Type: application/json" -d '{"name":"개발팀","parent_id":1}'
curl http://localhost:8000/departments/   # ← 최상위만 (본사)

# Recipe + 비용
curl -X POST http://localhost:8000/recipes/ -H "Content-Type: application/json" -d '{"product_id":1,"material_id":2,"quantity":0.5,"unit":"kg"}'
curl http://localhost:8000/recipes/product/1/cost
```

## 두 핵심 함정

### 1. 자기참조 `remote_side` 누락
```python
# 잘못: 어느 쪽이 부모인지 모름
parent = relationship("Department", back_populates="children")

# 올바름: id 컬럼이 부모 쪽임을 명시
parent = relationship("Department", remote_side="Department.id", back_populates="children")
```

### 2. Dual FK `foreign_keys=[col]` 누락
```python
# 잘못: Recipe 가 items 를 두 번 참조하는데 어느 FK 인지 모름 → AmbiguousForeignKeysError
product = relationship("Item")

# 올바름
product = relationship("Item", foreign_keys=[product_id])
```
