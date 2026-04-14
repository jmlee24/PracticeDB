# Day 3 워크북 — 주문 시스템 + 트랜잭션

## 사전 세팅

Docker PostgreSQL이 실행 중인 상태에서 아래 순서로 진행합니다.

```bash
# 서버 실행
uvicorn day3.main:app --reload

# 1) 카테고리 생성
curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "전자제품", "description": "IT 기기 및 부품"}'

# 2) 상품 A 생성 (재고 10개)
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "무선 마우스", "description": "2.4GHz 무선", "price": 25000, "stock": 10, "category_id": 1}'

# 3) 상품 B 생성 (재고 5개)
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "기계식 키보드", "description": "청축 풀배열", "price": 89000, "stock": 5, "category_id": 1}'
```

---

## TODO 해설

### TODO 17 — Order 모델 (★★☆)

`orders` 테이블을 정의합니다.

- `status` 기본값 `"pending"`: 주문 접수 상태를 나타내는 상태 머신의 초기값입니다.
- `total_amount` 기본값 `0`: 주문 생성 직후 items를 처리하며 누적하므로 초기값이 필요합니다.
- `items` relationship은 TODO 19와 함께 완성됩니다.

```python
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    items = relationship("OrderItem", back_populates="order")
```

### TODO 18 — OrderItem 모델 (★★☆)

`order_items` 테이블을 정의합니다.

- `unit_price`: **주문 시점의 가격을 고정** 저장합니다. 나중에 상품 가격이 바뀌어도 과거 주문 내역은 당시 가격을 유지해야 합니다.
- `order_id`, `product_id`는 각각 `orders.id`, `products.id`를 참조하는 외래키입니다.

```python
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
```

### TODO 19 — Order-OrderItem relationship (★☆☆)

양방향 relationship을 완성합니다.

- `Order.items` ↔ `OrderItem.order`: `back_populates`로 서로를 연결합니다.
- `OrderItem.product`: 단방향이므로 `back_populates` 없이 간단하게 설정합니다.

```python
# OrderItem 안에 추가
order = relationship("Order", back_populates="items")
product = relationship("Product")
```

### TODO 20 — OrderItemCreate (★☆☆)

클라이언트가 보내는 항목 데이터입니다. `unit_price`는 서버가 DB에서 조회하므로 요청에 포함하지 않습니다.

```python
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
```

### TODO 21 — OrderCreate (★★☆)

하나의 요청으로 여러 항목을 한꺼번에 주문합니다. `items`가 nested 리스트입니다.

```python
class OrderCreate(BaseModel):
    customer_name: str
    items: list[OrderItemCreate]
```

### TODO 22 — OrderItemResponse / OrderResponse (★★☆)

응답 스키마에서 `items: list[OrderItemResponse]`가 **nested 직렬화**의 핵심입니다.
`model_config = {"from_attributes": True}` 덕분에 ORM relationship이 자동으로 변환됩니다.

```python
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: int
    model_config = {"from_attributes": True}

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    status: str
    total_amount: int
    items: list[OrderItemResponse]
    created_at: datetime
    model_config = {"from_attributes": True}
```

### TODO 23 — POST / 주문 생성 (★★★)

트랜잭션의 핵심 로직입니다.

```python
@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    try:
        order = Order(customer_name=data.customer_name)
        db.add(order)
        db.flush()  # order.id를 얻기 위해 flush (commit 아님)

        total_amount = 0
        for item in data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"상품 ID {item.product_id}을(를) 찾을 수 없습니다")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"상품 '{product.name}'의 재고가 부족합니다")
            product.stock -= item.quantity
            db.add(OrderItem(order_id=order.id, product_id=item.product_id,
                             quantity=item.quantity, unit_price=product.price))
            total_amount += product.price * item.quantity

        order.total_amount = total_amount
        db.commit()
        db.refresh(order)
        return order
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 처리 중 오류가 발생했습니다")
```

### TODO 24 — GET / 주문 목록 (★★☆)

```python
@router.get("/", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()
```

### TODO 25 — GET /{order_id} 주문 단건 (★★☆)

```python
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order
```

### TODO 26 — DELETE /{order_id}/cancel 주문 취소 (★★★)

취소 시 차감했던 재고를 원복합니다. 이 역시 원자적으로 처리해야 합니다.

```python
@router.delete("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="이미 취소된 주문입니다")
    try:
        order.status = "cancelled"
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 취소 중 오류가 발생했습니다")
```

---

## 핵심 개념

### 트랜잭션 원자성 (Atomicity)

주문 생성 시 여러 테이블을 동시에 변경합니다.

```
Order INSERT
  ├── Product A stock -= 2
  ├── OrderItem A INSERT
  ├── Product B stock -= 1
  └── OrderItem B INSERT
```

중간 단계에서 오류가 나면 `db.rollback()`으로 **모든 변경을 없던 일로** 만들어야 합니다.
롤백하지 않으면 재고는 차감됐는데 주문은 없는 데이터 불일치가 발생합니다.

### db.flush() vs db.commit()

| 구분 | flush() | commit() |
|------|---------|---------|
| DB 반영 | 임시 반영 (트랜잭션 내부) | 영구 반영 |
| rollback 가능 | 가능 | 불가 |
| 사용 이유 | INSERT 후 생성된 id를 즉시 얻기 위해 | 모든 작업 완료 후 확정 |

### nested Pydantic 직렬화

```
OrderResponse
  └── items: list[OrderItemResponse]   ← ORM relationship이 자동 변환됨
```

`from_attributes=True`가 양쪽 스키마에 모두 있어야 중첩 직렬화가 동작합니다.

---

## 검증 체크리스트

```bash
# 1) 정상 주문 생성
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "홍길동", "items": [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}]}'
# 기대: 201, total_amount = 25000*2 + 89000*1 = 139000

# 2) 재고 부족 → 400 + 롤백 확인
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "테스터", "items": [{"product_id": 1, "quantity": 999}]}'
# 기대: 400, 재고 변동 없음

# 3) nested JSON 확인 — items 배열이 응답에 포함되는지
curl http://localhost:8000/orders/1
# 기대: items 배열에 product_id, quantity, unit_price 포함

# 4) 주문 취소 + 재고 원복
curl -X DELETE http://localhost:8000/orders/1/cancel
# 기대: status="cancelled"
curl http://localhost:8000/products/1
# 기대: stock이 주문 전 수량으로 복구됨

# 5) 없는 product_id → 404
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "테스터", "items": [{"product_id": 9999, "quantity": 1}]}'
# 기대: 404
```

---

## 다음: Day 4 — 페이지네이션

- `skip` / `limit` 쿼리 파라미터로 대용량 목록을 나눠 조회
- `order_by`로 정렬 기준 적용
- 전체 건수(`total`)와 현재 페이지 데이터를 함께 반환하는 응답 구조
