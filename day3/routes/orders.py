"""
주문 API 라우트 — TODO 23~26
==============================
트랜잭션의 핵심: 주문 생성 시 여러 테이블을 원자적으로 변경합니다.

원자성(Atomicity): 모든 작업이 성공하거나 모두 실패해야 함.
중간에 오류가 나면 db.rollback()으로 모든 변경을 되돌립니다.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day3.database import get_db
from day3.models import Order, OrderItem, Product
from day3.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


# ┌──────────────────────────────────────────────────┐
# │ [TODO 23] POST / — 주문 생성 + 트랜잭션 (★★★)    │
# │                                                    │
# │ 로직 순서:                                         │
# │ 1. Order 객체 생성 후 db.add()                     │
# │ 2. items 반복:                                     │
# │    a. product 존재 확인 (없으면 404)               │
# │    b. 재고 부족 확인 (quantity > stock → 400)      │
# │    c. product.stock -= item.quantity (재고 차감)   │
# │    d. OrderItem 생성 (unit_price=product.price)    │
# │    e. total_amount 누적                            │
# │ 3. order.total_amount 설정                         │
# │ 4. db.commit() + db.refresh(order)                 │
# │ 5. try/except: 오류 시 db.rollback() → 500 raise  │
# │                                                    │
# │ 왜 try/except가 필요한가?                           │
# │ commit() 전에 오류가 나면 세션 상태가 오염됩니다.   │
# │ rollback()으로 세션을 깨끗하게 되돌려야             │
# │ 이후 요청도 정상 처리됩니다.                        │
# └──────────────────────────────────────────────────┘
@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """주문 생성 — 재고 차감을 트랜잭션으로 처리"""
    try:
        order = Order(customer_name=data.customer_name)
        db.add(order)
        # flush: commit 없이 DB에 INSERT → order.id가 생성됨
        db.flush()

        total_amount = 0
        for item in data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"상품 ID {item.product_id}을(를) 찾을 수 없습니다",
                )
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"상품 '{product.name}'의 재고가 부족합니다 (현재 재고: {product.stock})",
                )

            # 재고 차감
            product.stock -= item.quantity

            # 주문 항목 생성 — 주문 시점 가격을 unit_price에 고정
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
            )
            db.add(order_item)
            total_amount += product.price * item.quantity

        order.total_amount = total_amount
        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        # HTTPException은 의도된 오류이므로 rollback 후 그대로 re-raise
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 처리 중 오류가 발생했습니다")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 24] GET / — 주문 목록 조회 (★★☆)            │
# │                                                    │
# │ 힌트: db.query(Order).all()                        │
# │ response_model=list[OrderResponse]                 │
# └──────────────────────────────────────────────────┘
@router.get("/", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    """주문 전체 목록 조회"""
    return db.query(Order).all()


# ┌──────────────────────────────────────────────────┐
# │ [TODO 25] GET /{order_id} — 주문 단건 조회 (★★☆) │
# │                                                    │
# │ - 없는 order_id → 404                              │
# │ - items(OrderItem 목록)도 함께 반환됨              │
# │   (relationship이 자동으로 로딩)                   │
# └──────────────────────────────────────────────────┘
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 단건 조회 (items 포함)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order


# ┌──────────────────────────────────────────────────┐
# │ [TODO 26] DELETE /{order_id}/cancel              │
# │           주문 취소 + 재고 원복 (★★★)             │
# │                                                    │
# │ 로직 순서:                                         │
# │ 1. 주문 조회 (없으면 404)                          │
# │ 2. 이미 cancelled이면 400                          │
# │ 3. order.status = "cancelled"                      │
# │ 4. 각 OrderItem 반복:                              │
# │    product.stock += item.quantity (재고 원복)      │
# │ 5. db.commit() + db.refresh(order)                 │
# │                                                    │
# │ 포인트: 취소도 원자적으로 처리해야 합니다.          │
# │ 일부만 원복되는 상황을 방지하려면 try/except 필요. │
# └──────────────────────────────────────────────────┘
@router.delete("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """주문 취소 — 재고를 원복하고 status를 cancelled로 변경"""
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
                # 취소 시 차감했던 재고를 돌려줌
                product.stock += item.quantity

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 취소 중 오류가 발생했습니다")
