"""
day7/complete/routes/work_orders.py — 상태머신 + BOM 자재 차감 (완성형, 줄단위 해설)
================================================================
이 파일이 Day 7 의 정수.

핵심 4가지:
    1) ALLOWED_TRANSITIONS dict — 상태 전이 규칙을 데이터로 표현
    2) start: BOM 검증 → 재고 검증 → 일괄 차감 (트랜잭션 원자성)
    3) complete: 완제품 재고 증가
    4) cancel: 진행 중이었으면 차감했던 자재 원복
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from day7.complete.database import get_db
from day7.complete.models import (
    WorkOrder, WorkOrderItem, Product, Process, BOMEntry,
)
from day7.complete.schemas import (
    WorkOrderCreate, WorkOrderResponse, WorkOrderItemResponse,
    ConsumeRequest,
)

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


# 상태 전이 규칙 — 키(현재 상태) → 가능한 다음 상태들의 리스트.
# COMPLETED/CANCELED 는 종착 상태(빈 리스트).
ALLOWED_TRANSITIONS = {
    "PENDING":     ["IN_PROGRESS", "CANCELED"],
    "IN_PROGRESS": ["COMPLETED", "CANCELED"],
    "COMPLETED":   [],
    "CANCELED":    [],
}


def _check_transition(current: str, next_: str) -> None:
    """허용되지 않은 전이는 400 으로 거절."""
    if next_ not in ALLOWED_TRANSITIONS.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"{current} → {next_} 전이는 허용되지 않습니다",
        )


def _to_response(wo: WorkOrder) -> WorkOrderResponse:
    """WorkOrderItemResponse 의 material_name 수동 주입."""
    return WorkOrderResponse(
        id=wo.id,
        order_number=wo.order_number,
        product_id=wo.product_id,
        process_id=wo.process_id,
        quantity=wo.quantity,
        status=wo.status,
        items=[
            WorkOrderItemResponse(
                id=it.id,
                material_id=it.material_id,
                material_name=it.material.name,
                required_qty=it.required_qty,
                consumed_qty=it.consumed_qty,
            )
            for it in wo.items
        ],
        created_at=wo.created_at,
        started_at=wo.started_at,
        completed_at=wo.completed_at,
    )


@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_work_order(data: WorkOrderCreate, db: Session = Depends(get_db)):
    """
    작업지시 생성:
        1) Product/Process 검증
        2) order_number 자동 생성 (timestamp)
        3) WorkOrder INSERT + flush → id 확보
        4) BOM 으로부터 WorkOrderItem 자동 생성 (quantity 곱셈)
        5) commit
    """
    if not db.query(Product).filter(Product.id == data.product_id).first():
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")
    if not db.query(Process).filter(Process.id == data.process_id).first():
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")

    try:
        order_number = f"WO-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        wo = WorkOrder(
            order_number=order_number,
            product_id=data.product_id,
            process_id=data.process_id,
            quantity=data.quantity,
            status="PENDING",
        )
        db.add(wo); db.flush()    # ← wo.id 확보 (commit 전)

        # BOM 으로부터 WorkOrderItem 자동 생성
        bom_entries = db.query(BOMEntry).filter(BOMEntry.product_id == data.product_id).all()
        for entry in bom_entries:
            db.add(WorkOrderItem(
                work_order_id=wo.id,
                material_id=entry.material_id,
                required_qty=entry.quantity * data.quantity,   # 1개당 소요 × 생산수량
                consumed_qty=0,
            ))

        db.commit(); db.refresh(wo)
        return _to_response(wo)
    except HTTPException:
        db.rollback(); raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업지시 생성 중 오류")


@router.get("/", response_model=list[WorkOrderResponse])
def list_work_orders(
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """status 는 대소문자 무관 (status.upper())."""
    query = db.query(WorkOrder)
    if status:
        query = query.filter(WorkOrder.status == status.upper())
    return [_to_response(wo) for wo in query.all()]


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """
    상태별 건수 + 완료된 작업의 총 생산량 (집계 함수 데모).
    """
    by_status = (
        db.query(WorkOrder.status, func.count(WorkOrder.id).label("count"))
        .group_by(WorkOrder.status)
        .all()
    )
    total_produced = (
        db.query(func.coalesce(func.sum(WorkOrder.quantity), 0))
        .filter(WorkOrder.status == "COMPLETED")
        .scalar()
    )
    return {
        "by_status": [{"status": s, "count": c} for s, c in by_status],
        "total_produced": total_produced,
    }


@router.get("/{wo_id}", response_model=WorkOrderResponse)
def get_work_order(wo_id: int, db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")
    return _to_response(wo)


@router.patch("/{wo_id}/start", response_model=WorkOrderResponse)
def start_work_order(wo_id: int, db: Session = Depends(get_db)):
    """
    작업 시작 — 자재 일괄 차감.

    실수 방지: '하나씩 차감하다 중간에 부족' 을 막기 위해
              먼저 전체 재고를 검증한 뒤 일괄 차감.
    """
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")
    _check_transition(wo.status, "IN_PROGRESS")

    try:
        # 1단계: 재고 검증 (차감 전 일괄 확인)
        for item in wo.items:
            if item.material.stock < item.required_qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"자재 '{item.material.name}' 재고 부족",
                )
        # 2단계: 일괄 차감
        for item in wo.items:
            item.material.stock -= item.required_qty

        wo.status = "IN_PROGRESS"
        wo.started_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(wo)
        return _to_response(wo)
    except HTTPException:
        db.rollback(); raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업 시작 중 오류")


@router.patch("/{wo_id}/complete", response_model=WorkOrderResponse)
def complete_work_order(wo_id: int, db: Session = Depends(get_db)):
    """완료 — 완제품 재고 증가."""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")
    _check_transition(wo.status, "COMPLETED")

    try:
        wo.product.stock += wo.quantity   # 완제품 재고 증가
        wo.status = "COMPLETED"
        wo.completed_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(wo)
        return _to_response(wo)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업 완료 중 오류")


@router.patch("/{wo_id}/cancel", response_model=WorkOrderResponse)
def cancel_work_order(wo_id: int, db: Session = Depends(get_db)):
    """
    취소 — 진행 중이었다면 차감한 자재 원복, PENDING 이었다면 원복 불필요.
    """
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")
    _check_transition(wo.status, "CANCELED")

    try:
        if wo.status == "IN_PROGRESS":
            # 차감했던 자재 원복
            for item in wo.items:
                item.material.stock += item.required_qty
        wo.status = "CANCELED"
        db.commit(); db.refresh(wo)
        return _to_response(wo)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업 취소 중 오류")


@router.post("/{wo_id}/consume", response_model=WorkOrderResponse)
def consume_material(wo_id: int, data: ConsumeRequest, db: Session = Depends(get_db)):
    """실적 등록 — 특정 자재의 실제 소비량 누적. required_qty 초과 금지."""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")
    if wo.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="진행 중인 작업만 실적 등록 가능")

    for item in wo.items:
        if item.material_id == data.material_id:
            if item.consumed_qty + data.consumed_qty > item.required_qty:
                raise HTTPException(status_code=400, detail="필요량 초과 소비 불가")
            item.consumed_qty += data.consumed_qty
            db.commit(); db.refresh(wo)
            return _to_response(wo)

    raise HTTPException(status_code=404, detail="해당 자재가 작업지시에 없습니다")
