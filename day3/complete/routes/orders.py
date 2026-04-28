"""
day3/complete/routes/orders.py — 주문 트랜잭션 (완성형, 줄단위 해설)
================================================================
이 파일이 Day 3 의 핵심. 트랜잭션 원자성 패턴 4종이 모두 들어있다:

    1) db.flush()     → commit 없이 INSERT 실행해 PK 확보
    2) try/except     → HTTPException 과 일반 Exception 분리 처리
    3) db.rollback()  → 어떤 단계에서 실패하든 전체 변경 무효화
    4) raise          → 의도된 에러는 그대로 재전송
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day3.complete.database import get_db
from day3.complete.models import Order, OrderItem, Product
from day3.complete.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """
    주문 생성 — 가장 복잡한 트랜잭션 패턴.

    실행 흐름:
        1) Order INSERT 대기
        2) flush → Order.id 즉시 확보 (commit 아님)
        3) for 각 item:
              상품 조회 → 없으면 404 (자동 rollback)
              재고 확인 → 부족하면 400 (자동 rollback)
              재고 차감 + OrderItem 추가
              total_amount 누적
        4) order.total_amount 갱신
        5) commit → 모든 INSERT/UPDATE 영구 반영
        6) refresh → DB가 채운 created_at 등 동기화

    어느 단계에서든 예외 발생 시 db.rollback() 으로 1)~5) 전부 무효화된다.
    """
    try:
        # 1) 주문 헤더 객체 생성 (메모리만)
        order = Order(customer_name=data.customer_name)
        db.add(order)
        db.flush()           # ← 여기서 INSERT 실행, order.id 즉시 사용 가능 (commit 아님)

        total_amount = 0
        for item in data.items:
            # 2) 상품 존재 확인
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"상품 ID {item.product_id} 을(를) 찾을 수 없습니다",
                )

            # 3) 재고 검증 (차감 전 — '차감 중 실패' 방지)
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"상품 '{product.name}' 의 재고가 부족합니다 (현재: {product.stock})",
                )

            # 4) 재고 차감 + 항목 추가 + 합계 누적
            product.stock -= item.quantity
            db.add(OrderItem(
                order_id=order.id,         # ← flush 덕분에 사용 가능
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,  # ← 주문 시점 가격 고정
            ))
            total_amount += product.price * item.quantity

        # 5) 합계 갱신 + 영구 반영
        order.total_amount = total_amount
        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        # 의도된 에러(404/400) → rollback 후 그대로 재전송 (FastAPI 가 응답으로 변환)
        db.rollback()
        raise
    except Exception:
        # 예상 못한 에러 → rollback + 500 으로 마스킹
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 처리 중 오류가 발생했습니다")


@router.get("/", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    """주문 목록. nested 응답: 각 주문에 items 배열이 자동 포함됨."""
    return db.query(Order).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order


@router.delete("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    주문 취소 — 차감했던 재고를 원복하는 역방향 트랜잭션.

    포인트: '이미 cancelled 인 주문' 을 재취소하면 재고가 두 번 더해지는 버그가 난다.
            이중 취소를 400 으로 막는다.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="이미 취소된 주문입니다")

    try:
        order.status = "cancelled"
        for item in order.items:               # relationship 으로 자동 로딩
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity  # 재고 원복
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="주문 취소 중 오류가 발생했습니다")
