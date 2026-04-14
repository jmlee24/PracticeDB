"""
작업지시 API 라우트 — Day 7 핵심
==================================
MES 작업지시(WorkOrder) + 상태머신 패턴.

상태 전이 규칙을 딕셔너리(ALLOWED_TRANSITIONS)로 중앙 관리합니다.
새로운 상태나 전이 규칙이 생겨도 딕셔너리 한 곳만 수정하면 됩니다.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from day7.database import get_db
from day7.models import WorkOrder, WorkOrderItem, Product, BOMEntry, Process
from day7.schemas import WorkOrderCreate, WorkOrderResponse, WorkOrderItemResponse

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

# 상태 전이 규칙 — 현재 상태 → 전이 가능한 상태 목록
# 딕셔너리로 관리하면 if/elif 체인 없이 O(1) 검증 가능
ALLOWED_TRANSITIONS = {
    "PENDING": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["COMPLETED", "CANCELLED"],
    "COMPLETED": [],
    "CANCELLED": [],
}


def _validate_transition(current_status: str, target_status: str) -> None:
    """상태 전이 유효성 검사 — 허용되지 않은 전이면 400 에러"""
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if target_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"'{current_status}' 상태에서 '{target_status}'(으)로 전이할 수 없습니다",
        )


def _build_work_order_response(work_order: WorkOrder) -> WorkOrderResponse:
    """WorkOrder ORM 객체를 WorkOrderResponse 스키마로 변환"""
    items = [
        WorkOrderItemResponse(
            id=item.id,
            material_id=item.material_id,
            # relationship을 통해 자재명을 함께 반환
            material_name=item.material.name,
            required_qty=item.required_qty,
            consumed_qty=item.consumed_qty,
        )
        for item in work_order.items
    ]
    return WorkOrderResponse(
        id=work_order.id,
        order_number=work_order.order_number,
        product_id=work_order.product_id,
        process_id=work_order.process_id,
        quantity=work_order.quantity,
        status=work_order.status,
        items=items,
        created_at=work_order.created_at,
        started_at=work_order.started_at,
        completed_at=work_order.completed_at,
    )


# ┌──────────────────────────────────────────────────┐
# │ [TODO 59] POST / — 작업지시 생성 (★★★)            │
# │                                                    │
# │ 로직:                                              │
# │ 1. product_id, process_id 존재 확인               │
# │ 2. BOM 조회 (product_id의 BOMEntry 목록)           │
# │ 3. order_number 자동 생성                          │
# │    예: f"WO-{datetime.now().strftime('%Y%m%d%H%M%S')}") │
# │ 4. WorkOrder 생성                                  │
# │ 5. BOM 항목별 WorkOrderItem 생성:                  │
# │    required_qty = bom.quantity * 작업지시 quantity │
# │ 6. commit                                          │
# └──────────────────────────────────────────────────┘
@router.post("/", response_model=WorkOrderResponse, status_code=201)
def create_work_order(data: WorkOrderCreate, db: Session = Depends(get_db)):
    """작업지시 생성 — BOM 기반 소요자재 자동 생성"""
    # 1. 완제품 존재 확인
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")

    # 2. 공정 존재 확인
    process = db.query(Process).filter(Process.id == data.process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")

    # 3. BOM 조회 — 이 완제품을 만들기 위한 자재 목록
    bom_entries = (
        db.query(BOMEntry)
        .filter(BOMEntry.product_id == data.product_id)
        .all()
    )

    # 4. order_number 자동 생성 — 동시 요청 충돌을 낮추기 위해 microsecond 포함
    order_number = f"WO-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    work_order = WorkOrder(
        order_number=order_number,
        product_id=data.product_id,
        process_id=data.process_id,
        quantity=data.quantity,
        status="PENDING",
    )
    db.add(work_order)
    # flush: commit 없이 PK(id) 확보 → WorkOrderItem의 work_order_id에 사용
    db.flush()

    # 5. BOM 항목별 WorkOrderItem 생성
    for bom in bom_entries:
        # 생산 수량에 비례해 소요량 계산 (BOM 단위수량 × 생산 목표 수량)
        item = WorkOrderItem(
            work_order_id=work_order.id,
            material_id=bom.material_id,
            required_qty=bom.quantity * data.quantity,
            consumed_qty=0,
        )
        db.add(item)

    db.commit()
    db.refresh(work_order)
    return _build_work_order_response(work_order)


# ┌──────────────────────────────────────────────────┐
# │ [TODO 60] GET / — 작업지시 목록 (★★☆)             │
# │                                                    │
# │ status 쿼리 파라미터로 필터링 가능                  │
# │ 예: GET /work-orders?status=PENDING                │
# └──────────────────────────────────────────────────┘
@router.get("/", response_model=list[WorkOrderResponse])
def list_work_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    """작업지시 목록 조회 — status 필터 지원"""
    query = db.query(WorkOrder)
    if status is not None:
        query = query.filter(WorkOrder.status == status.upper())
    work_orders = query.order_by(WorkOrder.created_at.desc()).all()
    return [_build_work_order_response(wo) for wo in work_orders]


# ┌──────────────────────────────────────────────────┐
# │ [TODO 61] PATCH /{work_order_id}/start           │
# │           작업 시작 (★★★)                         │
# │                                                    │
# │ 로직:                                              │
# │ 1. 상태 전이 검증 (PENDING → IN_PROGRESS만 허용)   │
# │ 2. 각 WorkOrderItem의 required_qty만큼             │
# │    material.stock 차감                             │
# │ 3. 재고 부족 시 400 + 롤백                         │
# │ 4. status = "IN_PROGRESS", started_at = now        │
# │ 5. commit                                          │
# └──────────────────────────────────────────────────┘
@router.patch("/{work_order_id}/start", response_model=WorkOrderResponse)
def start_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """작업 시작 — 소요자재 재고 차감 후 IN_PROGRESS로 전이"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")

    # 상태 전이 검증
    _validate_transition(work_order.status, "IN_PROGRESS")

    try:
        # 소요자재 재고 차감 — 하나라도 부족하면 전체 롤백
        for item in work_order.items:
            material = db.query(Product).filter(Product.id == item.material_id).first()
            if not material:
                raise HTTPException(
                    status_code=404,
                    detail=f"자재 ID {item.material_id}을(를) 찾을 수 없습니다",
                )
            if material.stock < item.required_qty:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"자재 '{material.name}'의 재고가 부족합니다 "
                        f"(필요: {item.required_qty}, 현재: {material.stock})"
                    ),
                )
            material.stock -= item.required_qty

        work_order.status = "IN_PROGRESS"
        work_order.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(work_order)
        return _build_work_order_response(work_order)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업 시작 처리 중 오류가 발생했습니다")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 62] PATCH /{work_order_id}/complete        │
# │           작업 완료 (★★★)                         │
# │                                                    │
# │ 로직:                                              │
# │ 1. 상태 전이 검증 (IN_PROGRESS → COMPLETED)        │
# │ 2. product.stock += work_order.quantity            │
# │    (완제품 재고 증가)                               │
# │ 3. status = "COMPLETED", completed_at = now        │
# └──────────────────────────────────────────────────┘
@router.patch("/{work_order_id}/complete", response_model=WorkOrderResponse)
def complete_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """작업 완료 — 완제품 재고 증가 후 COMPLETED로 전이"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")

    # 상태 전이 검증
    _validate_transition(work_order.status, "COMPLETED")

    try:
        # 완제품 재고 증가 — 생산된 수량만큼 stock에 반영
        product = db.query(Product).filter(Product.id == work_order.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")

        product.stock += work_order.quantity
        work_order.status = "COMPLETED"
        work_order.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(work_order)
        return _build_work_order_response(work_order)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업 완료 처리 중 오류가 발생했습니다")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 63] PATCH /{work_order_id}/cancel          │
# │           작업 취소 (★★★)                         │
# │                                                    │
# │ 로직:                                              │
# │ 1. ALLOWED_TRANSITIONS 검증                        │
# │ 2. IN_PROGRESS에서 취소:                           │
# │    자재 재고 원복 (required_qty만큼 stock 복원)     │
# │ 3. PENDING에서 취소: 재고 변동 없음                │
# │ 4. status = "CANCELLED"                            │
# └──────────────────────────────────────────────────┘
@router.patch("/{work_order_id}/cancel", response_model=WorkOrderResponse)
def cancel_work_order(work_order_id: int, db: Session = Depends(get_db)):
    """작업 취소 — IN_PROGRESS 상태에서는 자재 재고 원복"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")

    # 상태 전이 검증
    _validate_transition(work_order.status, "CANCELLED")

    try:
        # IN_PROGRESS 상태에서 취소 시 — 이미 차감한 자재 재고를 원복
        if work_order.status == "IN_PROGRESS":
            for item in work_order.items:
                material = db.query(Product).filter(Product.id == item.material_id).first()
                if material:
                    material.stock += item.required_qty

        # PENDING 상태에서 취소 시 — 아직 재고를 차감하지 않았으므로 원복 불필요

        work_order.status = "CANCELLED"
        db.commit()
        db.refresh(work_order)
        return _build_work_order_response(work_order)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="작업 취소 처리 중 오류가 발생했습니다")


# ┌──────────────────────────────────────────────────┐
# │ [TODO 64] PATCH /{work_order_id}/items/{item_id}/consume │
# │           실적 등록 (★★★) — 보너스                │
# │                                                    │
# │ consumed_qty 업데이트.                              │
# │ required_qty 초과 불가.                             │
# └──────────────────────────────────────────────────┘
@router.patch(
    "/{work_order_id}/items/{item_id}/consume",
    response_model=WorkOrderResponse,
)
def consume_material(
    work_order_id: int,
    item_id: int,
    consumed_qty: float,
    db: Session = Depends(get_db),
):
    """실적 등록 — 실제 소비한 자재 수량을 기록 (required_qty 초과 불가)"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="작업지시를 찾을 수 없습니다")

    # 작업 중(IN_PROGRESS) 상태에서만 실적 등록 가능
    if work_order.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="IN_PROGRESS 상태의 작업지시에만 실적을 등록할 수 있습니다",
        )

    item = (
        db.query(WorkOrderItem)
        .filter(WorkOrderItem.id == item_id, WorkOrderItem.work_order_id == work_order_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="소요자재 항목을 찾을 수 없습니다")

    # 필요량 초과 방지 — 실제 소비량이 BOM 기준 필요량을 넘으면 안 됨
    if consumed_qty > item.required_qty:
        raise HTTPException(
            status_code=400,
            detail=(
                f"소비량({consumed_qty})이 필요량({item.required_qty})을 초과할 수 없습니다"
            ),
        )

    item.consumed_qty = consumed_qty
    db.commit()
    db.refresh(work_order)
    return _build_work_order_response(work_order)


# ┌──────────────────────────────────────────────────┐
# │ [TODO 65] GET /dashboard — 대시보드 (★★★) — 보너스│
# │                                                    │
# │ 상태별 건수 집계 (group_by status)                 │
# │ 오늘 완료 수량 합계                                 │
# └──────────────────────────────────────────────────┘
@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """대시보드 — 상태별 작업지시 건수 + 오늘 완료 수량"""
    # 상태별 건수 집계 — group_by로 각 status의 count를 한 쿼리로 가져옴
    status_counts_raw = (
        db.query(WorkOrder.status, func.count(WorkOrder.id).label("count"))
        .group_by(WorkOrder.status)
        .all()
    )
    status_counts = {row.status: row.count for row in status_counts_raw}

    # 오늘 완료된 작업지시의 생산 수량 합계
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_completed_qty = (
        db.query(func.coalesce(func.sum(WorkOrder.quantity), 0))
        .filter(
            WorkOrder.status == "COMPLETED",
            WorkOrder.completed_at >= today_start,
        )
        .scalar()
    )

    return {
        "status_counts": status_counts,
        "today_completed_qty": today_completed_qty,
    }
