"""day4/complete/routes/orders.py — Day3 + 페이지네이션/status 필터."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.complete.database import get_db
from day4.complete.models import Order, OrderItem, Product
from day4.complete.schemas import OrderCreate, OrderResponse, PaginatedResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """Day3 와 동일한 트랜잭션 — 자세한 해설은 day4/complete README 참조."""
    try:
        order = Order(customer_name=data.customer_name)
        db.add(order); db.flush()
        total_amount = 0
        for item in data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"상품 ID {item.product_id} 없음")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"상품 '{product.name}' 재고 부족")
            product.stock -= item.quantity
            db.add(OrderItem(
                order_id=order.id, product_id=item.product_id,
                quantity=item.quantity, unit_price=product.price,
            ))
            total_amount += product.price * item.quantity
        order.total_amount = total_amount
        db.commit(); db.refresh(order)
        return order
    except HTTPException:
        db.rollback(); raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 처리 중 오류")


@router.get("/", response_model=PaginatedResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None, description="pending / cancelled 등"),
    db: Session = Depends(get_db),
):
    """주문 목록 페이지네이션 + 상태 필터."""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order
