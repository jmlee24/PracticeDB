"""
공정 API 라우트 — Day 6 신규
==============================
MES 도메인: 공정(Process) 트리 구조 CRUD.
자기참조 FK를 활용해 최상위 공정과 하위 공정을 관리합니다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day6.database import get_db
from day6.models import Process
from day6.schemas import ProcessCreate, ProcessResponse

router = APIRouter(prefix="/processes", tags=["processes"])


# ┌──────────────────────────────────────────────────┐
# │ [TODO 49] POST / — 공정 생성 (★★☆)               │
# │                                                    │
# │ 로직:                                              │
# │ 1. parent_id가 있으면 해당 공정이 존재하는지 확인  │
# │    → 없으면 404                                    │
# │ 2. parent_id가 None이면 최상위 공정으로 생성       │
# │ 3. Process 객체 생성 후 저장                       │
# │                                                    │
# │ 왜 parent 존재 확인이 필요한가?                    │
# │ DB FK 제약으로도 막히지만, 친절한 404 메시지를     │
# │ 돌려주기 위해 애플리케이션 레벨에서도 검증합니다.  │
# └──────────────────────────────────────────────────┘
@router.post("/", response_model=ProcessResponse, status_code=201)
def create_process(data: ProcessCreate, db: Session = Depends(get_db)):
    """공정 생성 — parent_id가 있으면 부모 공정 존재 확인"""
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


# ┌──────────────────────────────────────────────────┐
# │ [TODO 50] GET / — 공정 목록 조회 (★★☆)           │
# │                                                    │
# │ 쿼리 파라미터: parent_id (선택)                    │
# │                                                    │
# │ 동작:                                              │
# │ - parent_id 미전달: 최상위 공정만 반환             │
# │   (parent_id IS NULL)                              │
# │ - parent_id 전달: 해당 부모의 직속 하위 공정 반환  │
# │                                                    │
# │ 왜 기본값이 최상위인가?                             │
# │ 트리 탐색은 루트부터 시작하는 것이 자연스럽고       │
# │ 전체 트리를 한 번에 내려주면 응답이 비대해집니다.  │
# └──────────────────────────────────────────────────┘
@router.get("/", response_model=list[ProcessResponse])
def list_processes(
    parent_id: int | None = Query(default=None, description="부모 공정 ID (미전달 시 최상위 공정만 반환)"),
    db: Session = Depends(get_db),
):
    """공정 목록 조회 — parent_id 필터로 트리 탐색"""
    query = db.query(Process)
    if parent_id is None:
        # 최상위 공정: parent_id가 NULL인 레코드
        query = query.filter(Process.parent_id == None)  # noqa: E711
    else:
        query = query.filter(Process.parent_id == parent_id)
    return query.order_by(Process.sequence_order).all()
