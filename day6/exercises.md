# Day 6 워크북 — MES 공정 + BOM

## 도메인 개요

### 공정(Process)
제조의 각 단계를 트리 구조로 표현합니다.

```
SMT 실장 (최상위, sequence_order=1)
  ├── 부품 배치 (sequence_order=1)
  └── 납땜 (sequence_order=2)
검사 (최상위, sequence_order=2)
패키징 (최상위, sequence_order=3)
```

- 최상위 공정: `parent_id = NULL`
- 하위 공정: `parent_id = 부모 공정의 id`
- `sequence_order`: 같은 부모 아래에서의 실행 순서

### BOM (Bill of Materials)
완제품을 만들기 위한 자재 목록입니다.

```
PCB 보드 A타입 (완제품)
  ├── 저항 10K × 10ea
  ├── 커패시터 100uF × 5ea
  └── IC칩 ATmega328 × 1ea
```

### Material = Product 재활용
별도 테이블 없이 `Product` 테이블을 재사용합니다.
`category`로 "완제품"과 "원자재"를 구분합니다.

```
categories
  ├── id=1, name="완제품"
  └── id=2, name="원자재"

products
  ├── id=1, name="PCB 보드 A타입", category_id=1  (완제품)
  ├── id=2, name="저항 10K",       category_id=2  (원자재)
  ├── id=3, name="커패시터 100uF", category_id=2  (원자재)
  └── id=4, name="IC칩 ATmega328", category_id=2  (원자재)
```

---

## 사전 세팅

Docker PostgreSQL이 실행 중인 상태에서 아래 순서로 진행합니다.

```bash
# 서버 실행
uvicorn day6.main:app --reload

# 1) 카테고리 생성
curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "완제품", "description": "제조 완성품"}'

curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "원자재", "description": "제조에 투입되는 재료"}'

# 2) 완제품 등록 (category_id=1)
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "PCB 보드 A타입", "price": 15000, "stock": 100, "category_id": 1}'

# 3) 자재 3종 등록 (category_id=2)
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "저항 10K", "price": 50, "stock": 10000, "category_id": 2}'

curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "커패시터 100uF", "price": 200, "stock": 5000, "category_id": 2}'

curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "IC칩 ATmega328", "price": 3000, "stock": 500, "category_id": 2}'
```

---

## TODO 해설

### TODO 42 — Process 모델 (★★☆)

자기참조 FK로 트리 구조를 구현합니다.

```python
class Process(Base):
    __tablename__ = "processes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("processes.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

`parent_id`가 `NULL`인 레코드가 최상위 공정입니다.
같은 테이블(`processes.id`)을 참조하는 것이 자기참조 FK의 핵심입니다.

### TODO 43 — Process 자기참조 relationship (★★☆)

```python
children = relationship("Process", back_populates="parent")
parent = relationship("Process", back_populates="children", remote_side=[id])
```

`remote_side=[id]`의 의미:
- "부모" 역할을 하는 쪽의 컬럼이 `id`임을 명시합니다.
- `parent_id → processes.id` 방향에서 `id` 쪽이 one(부모), `parent_id` 쪽이 many(자식)입니다.
- SQLAlchemy는 자기참조 시 어느 쪽이 "one"인지 스스로 판단하지 못하므로 `remote_side`로 명시합니다.

### TODO 44 — BOMEntry 모델 (★★☆)

```python
class BOMEntry(Base):
    __tablename__ = "bom_entries"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="ea")

    product = relationship("Product", foreign_keys=[product_id])
    material = relationship("Product", foreign_keys=[material_id])
```

`foreign_keys` 명시가 필요한 이유:
같은 테이블(`products`)을 두 FK로 참조하므로 SQLAlchemy가 어느 FK를 쓸지 스스로 판단하지 못합니다.
각 `relationship`에 `foreign_keys`를 명시해 연결할 FK를 지정합니다.

### TODO 45 — ProcessCreate (★☆☆)

```python
class ProcessCreate(BaseModel):
    name: str
    description: str | None = None
    sequence_order: int
    parent_id: int | None = None
```

`parent_id`의 기본값이 `None`이므로 미전달 시 최상위 공정이 됩니다.

### TODO 46 — ProcessResponse (★★☆)

```python
class ProcessResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    sequence_order: int
    parent_id: int | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

### TODO 47 — BOMEntryCreate (★☆☆)

```python
class BOMEntryCreate(BaseModel):
    product_id: int
    material_id: int
    quantity: float
    unit: str = "ea"
```

### TODO 48 — BOMEntryResponse (★★☆)

```python
class BOMEntryResponse(BaseModel):
    id: int
    product_id: int
    material_id: int
    material_name: str   # ORM에 없는 필드 — API 레이어에서 수동 주입
    quantity: float
    unit: str

    model_config = {"from_attributes": True}
```

`material_name`은 `BOMEntry` ORM 객체의 속성이 아닙니다.
`entry.material.name`에서 꺼내어 수동으로 설정합니다:

```python
BOMEntryResponse(
    id=entry.id,
    product_id=entry.product_id,
    material_id=entry.material_id,
    material_name=entry.material.name,
    quantity=entry.quantity,
    unit=entry.unit,
)
```

### TODO 49 — POST /processes/ 공정 생성 (★★☆)

```python
@router.post("/", response_model=ProcessResponse, status_code=201)
def create_process(data: ProcessCreate, db: Session = Depends(get_db)):
    if data.parent_id is not None:
        parent = db.query(Process).filter(Process.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="부모 공정을 찾을 수 없습니다")

    process = Process(
        name=data.name,
        description=data.description,
        sequence_order=data.sequence_order,
        parent_id=data.parent_id,
    )
    db.add(process)
    db.commit()
    db.refresh(process)
    return process
```

### TODO 50 — GET /processes/ 공정 목록 (★★☆)

```python
@router.get("/", response_model=list[ProcessResponse])
def list_processes(
    parent_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Process)
    if parent_id is None:
        query = query.filter(Process.parent_id == None)
    else:
        query = query.filter(Process.parent_id == parent_id)
    return query.order_by(Process.sequence_order).all()
```

`parent_id`가 없으면 `IS NULL` 필터로 최상위 공정만 반환합니다.

### TODO 51 — POST /bom/ BOM 항목 등록 (★★☆)

```python
@router.post("/", response_model=BOMEntryResponse, status_code=201)
def create_bom_entry(data: BOMEntryCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")

    material = db.query(Product).filter(Product.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="자재를 찾을 수 없습니다")

    if data.product_id == data.material_id:
        raise HTTPException(status_code=400, detail="완제품과 자재가 동일할 수 없습니다")

    entry = BOMEntry(...)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return BOMEntryResponse(..., material_name=entry.material.name)
```

### TODO 52 — GET /bom/product/{product_id} 제품별 BOM 조회 (★★★)

```python
@router.get("/product/{product_id}", response_model=list[BOMEntryResponse])
def get_bom_by_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")

    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()
    return [
        BOMEntryResponse(
            id=entry.id,
            product_id=entry.product_id,
            material_id=entry.material_id,
            material_name=entry.material.name,
            quantity=entry.quantity,
            unit=entry.unit,
        )
        for entry in entries
    ]
```

### TODO 53 — GET /bom/product/{product_id}/cost 총 자재 비용 (★★★)

```python
@router.get("/product/{product_id}/cost")
def get_bom_cost(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")

    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()

    items = []
    total_cost = 0.0
    for entry in entries:
        subtotal = entry.material.price * entry.quantity
        total_cost += subtotal
        items.append({
            "material_name": entry.material.name,
            "quantity": entry.quantity,
            "unit": entry.unit,
            "unit_price": entry.material.price,
            "subtotal": subtotal,
        })

    return {
        "product_id": product.id,
        "product_name": product.name,
        "total_cost": total_cost,
        "items": items,
    }
```

---

## 핵심 개념

### 자기참조 FK (Self-referential FK)

```
processes 테이블
┌─────┬──────────────┬────────────┬──────────┐
│ id  │ name         │ parent_id  │ seq_ord  │
├─────┼──────────────┼────────────┼──────────┤
│  1  │ SMT 실장     │   NULL     │    1     │  ← 최상위
│  2  │ 부품 배치    │     1      │    1     │  ← id=1의 자식
│  3  │ 납땜         │     1      │    2     │  ← id=1의 자식
│  4  │ 검사         │   NULL     │    2     │  ← 최상위
└─────┴──────────────┴────────────┴──────────┘
```

### remote_side 동작 원리

```python
parent = relationship("Process", back_populates="children", remote_side=[id])
```

SQLAlchemy는 JOIN 시 어느 쪽이 "one"(부모)이고 어느 쪽이 "many"(자식)인지 알아야 합니다.
자기참조에서는 두 쪽 모두 같은 테이블이므로 `remote_side`로 명시합니다.
`remote_side=[id]`는 "id 컬럼이 있는 레코드가 부모(one) 역할"이라는 의미입니다.

### foreign_keys 지정

```python
product = relationship("Product", foreign_keys=[product_id])
material = relationship("Product", foreign_keys=[material_id])
```

`BOMEntry`가 `products.id`를 두 번 참조하므로 각 relationship에 사용할 FK를 명시합니다.
명시하지 않으면 SQLAlchemy가 `AmbiguousForeignKeysError`를 발생시킵니다.

### BOM 패턴

완제품과 자재를 별도 테이블로 분리하지 않고 `category`로 구분하는 패턴입니다.
- 장점: 스키마 단순화, 공통 속성(name, price, stock) 공유
- 단점: category 오용 시 완제품이 자재로 잘못 등록될 수 있음 → 애플리케이션 레이어 검증 필요

---

## 검증 체크리스트

```bash
# 1) 최상위 공정 생성
curl -X POST http://localhost:8000/processes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "SMT 실장", "sequence_order": 1}'
# 기대: 201, parent_id=null

# 2) 하위 공정 생성 (parent_id=1)
curl -X POST http://localhost:8000/processes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "부품 배치", "sequence_order": 1, "parent_id": 1}'
# 기대: 201, parent_id=1

# 3) 없는 parent_id → 404
curl -X POST http://localhost:8000/processes/ \
  -H "Content-Type: application/json" \
  -d '{"name": "테스트", "sequence_order": 1, "parent_id": 9999}'
# 기대: 404

# 4) BOM 항목 등록
curl -X POST http://localhost:8000/bom/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "material_id": 2, "quantity": 10, "unit": "ea"}'
# 기대: 201, material_name="저항 10K"

# 5) 총 자재 비용 조회
curl http://localhost:8000/bom/product/1/cost
# 기대: total_cost = 저항(50*10) + 커패시터(200*5) + IC칩(3000*1) = 4500
```

---

## 다음: Day 7 — 작업지시 + 상태머신

- `WorkOrder` (작업지시): 어떤 공정을, 언제, 얼마나 수행할지 지시
- 상태머신: `pending → in_progress → completed / cancelled`
- 상태 전이 규칙: 허용된 전이만 가능하도록 애플리케이션 레이어 검증
- `Event` 로그: 상태 변경 이력 추적
