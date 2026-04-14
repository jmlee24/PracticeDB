# Day 2 워크북 — 상품 + 외래키(FK)

## 환경 세팅 & 서버 실행

```bash
# 1. PostgreSQL 컨테이너 실행
docker compose up -d

# 2. 의존성 설치 (최초 1회)
pip install -r requirements.txt

# 3. 서버 실행
uvicorn day2.main:app --reload
```

실행 후 확인:
- Swagger UI: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

---

## DB 초기화 절차

테이블 구조를 새로 적용하고 싶을 때:

```bash
# PostgreSQL 컨테이너에 접속
docker compose exec db psql -U study -d studydb

# 기존 테이블 삭제 (순서 중요 — FK 참조 방향 역순)
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

# 접속 종료
\q

# 서버 재시작 시 테이블 자동 재생성
uvicorn day2.main:app --reload
```

---

## TODO 목록

| 번호 | 파일 | 내용 | 난이도 |
|------|------|------|--------|
| TODO 6 | `models.py` | Product.description 컬럼 추가 | ★☆☆ |
| TODO 7 | `models.py` | Product.stock 컬럼 추가 | ★☆☆ |
| TODO 8 | `models.py` | Product.category_id 외래키 추가 | ★★☆ |
| TODO 9 | `models.py` | Product.category relationship 설정 | ★★☆ |
| TODO 10 | `schemas.py` | ProductCreate 필드 5개 정의 | ★☆☆ |
| TODO 11 | `schemas.py` | ProductResponse 필드 8개 + model_config | ★☆☆ |
| TODO 12 | `routes/products.py` | 상품 생성 (FK 검증 포함) | ★★☆ |
| TODO 13 | `routes/products.py` | 상품 목록 조회 (category_id 필터) | ★★☆ |
| TODO 14 | `routes/products.py` | 상품 단건 조회 | ★☆☆ |
| TODO 15 | `routes/products.py` | 상품 수정 (FK 검증 + 업데이트) | ★★★ |
| TODO 16 | `routes/products.py` | 상품 삭제 | ★☆☆ |

---

## 각 TODO 해설

### TODO 6 — description 컬럼 (models.py)

`Category.description`과 동일한 패턴입니다.

```python
description = Column(Text, nullable=True)
```

Text 타입은 길이 제한 없는 문자열입니다. `nullable=True`이므로 생략 가능합니다.

---

### TODO 7 — stock 컬럼 (models.py)

재고 수량을 저장하는 정수형 컬럼입니다. 기본값 0으로 설정합니다.

```python
stock = Column(Integer, nullable=False, default=0)
```

---

### TODO 8 — category_id 외래키 (models.py)

외래키(ForeignKey)는 다른 테이블의 행을 참조합니다.
형식: `ForeignKey("테이블명.컬럼명")`

```python
category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
```

`ForeignKey("categories.id")` — `categories` 테이블의 `id` 컬럼을 참조한다는 의미입니다.
DB 수준에서 존재하지 않는 category_id 삽입을 막아줍니다.

---

### TODO 9 — category relationship (models.py)

`relationship`은 Python 코드 수준에서 연관 객체에 접근할 수 있게 해줍니다.
`back_populates`로 양방향 연결을 설정합니다.

```python
category = relationship("Category", back_populates="products")
```

- `Product.category` → 이 상품이 속한 카테고리 객체
- `Category.products` → 이 카테고리에 속한 상품 목록

`back_populates`의 값은 상대 모델에서 이 모델을 가리키는 속성명과 일치해야 합니다.

---

### TODO 10 — ProductCreate (schemas.py)

`CategoryCreate`를 참고해서 5개 필드를 정의합니다.

```python
name: str
description: str | None = None
price: int
stock: int = 0
category_id: int
```

필수 필드(기본값 없음): `name`, `price`, `category_id`
선택 필드(기본값 있음): `description`, `stock`

---

### TODO 11 — ProductResponse (schemas.py)

응답 스키마는 DB에서 읽어온 모든 필드를 포함합니다.
`CategoryResponse`를 참고하고 `model_config`도 잊지 마세요.

```python
id: int
name: str
description: str | None
price: int
stock: int
category_id: int
created_at: datetime
updated_at: datetime

model_config = {"from_attributes": True}
```

---

### TODO 12 — 상품 생성 (routes/products.py)

`categories.py`의 `create_category`에 **FK 유효성 검사**가 추가된 버전입니다.

```python
@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    # 1. 카테고리 존재 확인 (FK 검증)
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    # 2. 상품 생성
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
```

왜 FK 검증이 필요한가?
DB는 존재하지 않는 category_id 삽입을 막아주지만,
사전에 확인해서 명확한 404 메시지를 반환하는 것이 좋은 API 설계입니다.

---

### TODO 13 — 상품 목록 조회 (routes/products.py)

`category_id` 쿼리 파라미터로 조건부 필터링합니다.
`categories.py`의 `list_categories`에서 `is_active` 필터 패턴과 동일합니다.

```python
@router.get("/", response_model=list[ProductResponse])
def list_products(
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    return query.all()
```

- `GET /products` → 전체 상품
- `GET /products?category_id=1` → category_id=1인 상품만

---

### TODO 14 — 상품 단건 조회 (routes/products.py)

`categories.py`의 `get_category`와 완전히 동일한 패턴입니다.

```python
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product
```

---

### TODO 15 — 상품 수정 (routes/products.py)

가장 복잡한 TODO입니다. **TODO 12의 FK 검증** + **update 패턴** 조합입니다.

```python
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
):
    # 1. 기존 상품 조회
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # 2. 새 category_id FK 검증 (카테고리를 바꾸는 경우)
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    # 3. 모든 필드 업데이트
    product.name = data.name
    product.description = data.description
    product.price = data.price
    product.stock = data.stock
    product.category_id = data.category_id
    db.commit()
    db.refresh(product)
    return product
```

---

### TODO 16 — 상품 삭제 (routes/products.py)

`categories.py`의 `delete_category`와 동일한 패턴입니다.

```python
@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    db.delete(product)
    db.commit()
```

---

## 검증 체크리스트

TODO를 모두 완성한 뒤 아래 5가지를 Swagger UI(`/docs`)에서 확인하세요.

- [ ] **카테고리 생성** → `POST /categories` 로 카테고리를 1개 만들고 `id`를 확인한다
- [ ] **상품 생성 성공** → 위 `category_id`로 `POST /products` 를 호출하면 201 응답이 온다
- [ ] **상품 생성 실패** → 존재하지 않는 `category_id`(예: 9999)로 시도하면 404가 온다
- [ ] **카테고리 필터** → `GET /products?category_id=1` 이 해당 카테고리 상품만 반환한다
- [ ] **상품 수정** → `PUT /products/{id}` 로 price를 바꾸면 응답에 변경값이 반영된다

---

## 다음 단계

Day 3에서는 **주문 + 트랜잭션**을 다룹니다.

- 주문 생성 시 여러 테이블에 동시에 데이터를 써야 할 때 트랜잭션으로 원자성을 보장합니다
- 재고 차감과 주문 삽입이 하나의 트랜잭션으로 묶이지 않으면 어떤 문제가 생기는지 배웁니다
