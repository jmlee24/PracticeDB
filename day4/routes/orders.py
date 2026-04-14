"""
주문 API 라우트 — Day 3 완성본 + TODO 33
==========================================
트랜잭션의 핵심: 주문 생성 시 여러 테이블을 원자적으로 변경합니다.

원자성(Atomicity): 모든 작업이 성공하거나 모두 실패해야 함.
중간에 오류가 나면 db.rollback()으로 모든 변경을 되돌립니다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.database import get_db
from day4.models import Order, OrderItem, Product
from day4.schemas import OrderCreate, OrderResponse, PaginatedResponse

router = APIRouter(prefix="/orders", tags=["orders"])


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
# │ [TODO 33] 주문 목록 페이지네이션 + status 필터 (★★☆)│
# │                                                    │
# │ 기존 list_orders를 개선하세요.                     │
# │                                                    │
# │ 추가 파라미터:                                     │
# │ - page: int = Query(default=1, ge=1)               │
# │ - size: int = Query(default=10, ge=1, le=100)      │
# │ - status: str | None = Query(default=None)         │
# │   (pending / cancelled 등 상태로 필터)              │
# │                                                    │
# │ 로직:                                              │
# │   query = db.query(Order)                          │
# │   if status:                                       │
# │       query = query.filter(Order.status == status) │
# │   total = query.count()                            │
# │   offset = (page - 1) * size                       │
# │   items = query.offset(offset).limit(size).all()   │
# │                                                    │
# │ 반환: PaginatedResponse                            │
# └──────────────────────────────────────────────────┘
@router.get("/", response_model=PaginatedResponse)
def list_orders(
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
    status: str | None = Query(default=None, description="주문 상태 필터 (pending, cancelled)"),
    db: Session = Depends(get_db),
):
    """주문 목록 조회 — 페이지네이션 + 상태 필터"""
    query = db.query(Order)

    # status 필터 — 값이 있을 때만 적용
    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()

    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 단건 조회 (items 포함)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order


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
