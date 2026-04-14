# Day 1 — CRUD 기초 워크북

## 환경 세팅

### 1. DB 컨테이너 실행
```bash
docker compose up -d
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
uvicorn day1.main:app --reload
```

Swagger UI: http://localhost:8000/docs

---

## DB 초기화 절차

서버를 처음 실행하면 `Base.metadata.create_all(bind=engine)`이 자동으로 테이블을 생성합니다.  
별도의 마이그레이션 명령 없이 `uvicorn` 실행만으로 테이블이 준비됩니다.

---

## TODO 목록

| 번호 | 파일 | 난이도 | 설명 |
|------|------|--------|------|
| TODO 1 | `day1/main.py` | ★☆☆ | health 엔드포인트에 DB 연결 상태 확인 추가 |
| TODO 2 | `day1/models.py` | ★☆☆ | Category 모델에 `is_active` Boolean 컬럼 추가 |
| TODO 3 | `day1/schemas.py` | ★☆☆ | `CategoryCreate`에 `is_active` 필드 추가 |
| TODO 4 | `day1/schemas.py` | ★☆☆ | `CategoryResponse`에 `is_active` 필드 추가 |
| TODO 5 | `day1/routes/categories.py` | ★☆☆ | 카테고리 목록 조회에 `is_active` 쿼리 필터 추가 |

---

## TODO 해설

### TODO 1 — `day1/main.py` ★☆☆

**목표**: `/health` 엔드포인트가 DB 연결 여부도 함께 반환하도록 수정

**핵심 개념**:
- `Depends(get_db)`: FastAPI의 Dependency Injection으로 DB 세션을 함수에 주입
- `text("SELECT 1")`: SQLAlchemy에서 raw SQL을 실행할 때 `text()`로 감싸야 함
- `try/except`로 연결 실패 시 graceful하게 처리

**완성 후 응답 예시**:
```json
{"status": "ok", "db": "connected"}
```

---

### TODO 2 — `day1/models.py` ★☆☆

**목표**: `Category` 모델에 `is_active` 컬럼 추가

**핵심 개념**:
- **소프트 삭제(soft delete)**: 레코드를 실제로 삭제하지 않고 `is_active=False`로 비활성화하는 패턴
- DB에서 데이터를 물리적으로 지우면 복구가 어렵기 때문에, 활성/비활성 플래그로 관리하는 방식이 실무에서 널리 쓰임

**추가할 코드**:
```python
is_active = Column(Boolean, nullable=False, default=True)
```

---

### TODO 3 — `day1/schemas.py` ★☆☆

**목표**: `CategoryCreate` 스키마에 `is_active` 필드 추가

**핵심 개념**:
- Pydantic 필드의 기본값: `is_active: bool = True`로 선언하면 클라이언트가 이 필드를 생략해도 `True`로 처리됨
- 기본값 덕분에 기존 API 호출 코드를 변경하지 않아도 호환성 유지 가능

**추가할 코드**:
```python
is_active: bool = True
```

---

### TODO 4 — `day1/schemas.py` ★☆☆

**목표**: `CategoryResponse` 스키마에 `is_active` 필드 추가

**핵심 개념**:
- Response 스키마는 DB에서 읽어온 값을 그대로 반환하므로 기본값 불필요
- `model_config = {"from_attributes": True}` 설정이 있어야 ORM 객체를 Pydantic 모델로 변환 가능

**추가할 코드**:
```python
is_active: bool
```

---

### TODO 5 — `day1/routes/categories.py` ★☆☆

**목표**: `GET /categories` 엔드포인트에 `is_active` 쿼리 파라미터 필터 추가

**핵심 개념**:
- `Query(default=None)`: 쿼리 파라미터를 선택적으로 받을 때 사용. `None`이면 필터 없이 전체 조회
- 조건부 `filter()`: `is_active`가 `None`이 아닐 때만 필터를 적용하는 패턴

**완성 후 동작**:
- `GET /categories` → 전체 조회
- `GET /categories?is_active=true` → 활성 카테고리만 조회
- `GET /categories?is_active=false` → 비활성 카테고리만 조회

**완성 코드 예시**:
```python
def list_categories(
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Category)
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    return query.all()
```

> 참고: Day 2의 `products.py`에서도 동일한 패턴을 사용합니다. 여기서 충분히 익혀두세요.

---

## 검증 체크리스트

TODO를 모두 완성했다면 아래 항목을 순서대로 확인하세요.

- [ ] `GET /health` → `{"status": "ok", "db": "connected"}` 반환
- [ ] `POST /categories` 요청 body에 `is_active` 필드 전달 가능
- [ ] `GET /categories?is_active=true` → 활성 카테고리만 필터링되어 반환
- [ ] `GET /categories?is_active=false` → 비활성 카테고리만 반환
- [ ] Swagger UI(`http://localhost:8000/docs`)에서 Category CRUD 5개 엔드포인트 모두 정상 동작

---

## 다음 단계 예고

**Day 2**에서는 외래키(Foreign Key)로 테이블 간 관계를 설정합니다.

- `Product` 모델이 `Category`를 참조하는 1:N 관계 구현
- `relationship()`으로 ORM 레벨에서 연관 객체 접근
- `GET /categories?is_active=true` 같은 필터 패턴을 `products.py`에도 적용
