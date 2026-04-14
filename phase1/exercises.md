# Phase 1 연습문제 가이드

## 시작하기 전에

### 환경 세팅
```bash
# 1. PostgreSQL 실행 (Docker 필요)
docker compose up -d

# 2. 파이썬 가상환경 생성 & 활성화
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash

# 3. 패키지 설치
pip install -r requirements.txt
```

### 서버 실행
```bash
# StudyDB 폴더에서 실행
uvicorn phase1.main:app --reload
```
- `--reload`: 코드 수정 시 자동 재시작
- 실행 후 http://localhost:8000/docs 에서 Swagger UI로 API 테스트 가능

---

## 문제 풀이 순서

TODO를 순서대로 풀어야 합니다. 모델 → 스키마 → 라우트 순서.

### 파일별 위치

| TODO | 파일 | 난이도 | 설명 |
|------|------|--------|------|
| 1 | `models.py` | ★☆☆ | description 컬럼 추가 |
| 2 | `models.py` | ★☆☆ | stock 컬럼 추가 (기본값 포함) |
| 3 | `models.py` | ★★☆ | 외래키(FK) 컬럼 추가 |
| 4 | `models.py` | ★★☆ | relationship 설정 |
| 5 | `schemas.py` | ★☆☆ | ProductCreate 필드 정의 |
| 6 | `schemas.py` | ★☆☆ | ProductResponse 필드 정의 |
| 7 | `routes/products.py` | ★★☆ | 상품 생성 API (FK 검증 포함) |
| 8 | `routes/products.py` | ★★☆ | 목록 조회 API (필터링) |
| 9 | `routes/products.py` | ★☆☆ | 단건 조회 API |
| 10 | `routes/products.py` | ★★★ | 상품 수정 API (FK 검증 + 업데이트) |
| 11 | `routes/products.py` | ★☆☆ | 상품 삭제 API |

---

## 각 문제 해설

### TODO 1~2: 컬럼 추가 (models.py)
Category 모델이 완성된 예시입니다. 같은 패턴으로 Product에 컬럼을 추가하세요.

**핵심 개념**: `Column(타입, nullable=..., default=...)`
- `nullable=False` → NOT NULL 제약조건
- `default=값` → INSERT 시 값을 안 주면 자동으로 채워짐

### TODO 3: 외래키 (models.py)
외래키는 두 테이블을 연결하는 핵심입니다.

**핵심 개념**: `ForeignKey("테이블명.컬럼명")`
- 참조하는 테이블의 **실제 테이블명** (클래스명 아님!)을 씁니다
- `categories` 테이블의 `id` 컬럼을 참조 → `ForeignKey("categories.id")`

### TODO 4: Relationship (models.py)
FK가 물리적 연결이라면, relationship은 파이썬 레벨의 논리적 연결입니다.

**핵심 개념**: `relationship("대상클래스명", back_populates="상대쪽필드명")`
- FK 컬럼이 있는 쪽(Product) → 단일 객체 (`category`)
- FK 컬럼이 없는 쪽(Category) → 리스트 (`products`)

### TODO 5~6: Pydantic 스키마 (schemas.py)
ORM 모델과 API 스키마를 분리하는 이유를 이해하는 문제입니다.

**핵심 개념**:
- Create 스키마: 클라이언트가 **보내는** 데이터 (id, created_at 없음)
- Response 스키마: 서버가 **응답하는** 데이터 (id, created_at 포함)
- `model_config = {"from_attributes": True}`: ORM 객체 → Pydantic 자동 변환

### TODO 7: 상품 생성 + FK 검증 (routes/products.py)
카테고리 생성과 비슷하지만, **외래키 유효성 검사**가 추가됩니다.

**핵심 개념**: 존재하지 않는 category_id로 상품을 만들면 안 됨
```python
# FK 검증 패턴
category = db.query(Category).filter(Category.id == data.category_id).first()
if not category:
    raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
```

### TODO 8: 필터링이 있는 목록 조회 (routes/products.py)
조건부 필터링은 실무에서 가장 많이 쓰는 패턴입니다.

**핵심 개념**: 쿼리를 점진적으로 조립하기
```python
query = db.query(Product)         # 기본 쿼리
if 조건:
    query = query.filter(...)     # 조건 추가
return query.all()                # 실행
```

### TODO 9, 11: 단건 조회 & 삭제
categories.py의 해당 함수와 동일한 패턴입니다. 복붙 후 모델명만 바꾸면 됩니다.

### TODO 10: 상품 수정 (가장 어려움)
생성(TODO 7)의 FK 검증 + 수정(update_category) 패턴의 조합입니다.

---

## 검증 방법

모든 TODO를 완성한 후:

1. 서버 실행: `uvicorn phase1.main:app --reload`
2. http://localhost:8000/docs 접속
3. 아래 순서로 테스트:

```
1. POST /categories  → 카테고리 생성 {"name": "전자부품", "description": "각종 전자부품"}
2. GET  /categories  → 생성 확인
3. POST /products    → 상품 생성 {"name": "저항 10K", "price": 100, "stock": 500, "category_id": 1}
4. GET  /products    → 전체 조회
5. GET  /products?category_id=1 → 필터링 조회
6. GET  /products/1  → 단건 조회
7. PUT  /products/1  → 수정 {"name": "저항 10K (수정)", "price": 150, "stock": 450, "category_id": 1}
8. DELETE /products/1 → 삭제
9. GET  /products/1  → 404 확인
```

모두 정상 동작하면 Phase 1 완료!

---

## 다음 단계 (Phase 2 예고)

Phase 1을 완성하면 다음을 다룹니다:
- 주문/주문상세 (1:N 관계를 API로 다루기)
- 트랜잭션 (주문 생성 시 재고 차감 — 하나 실패하면 전체 롤백)
- 페이지네이션, 정렬
- nested JSON 응답 (주문 안에 상품 정보 포함)
