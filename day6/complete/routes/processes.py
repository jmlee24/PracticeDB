"""
day6/complete/routes/processes.py — 자기참조 공정 CRUD (완성형)
================================================================
parent_id 가 NULL 이면 최상위 공정, 값이 있으면 하위 공정.
parent_id 가 들어오면 해당 부모가 실제 존재하는지 사전 검증해 명확한 404 반환.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day6.complete.database import get_db
from day6.complete.models import Process
from day6.complete.schemas import ProcessCreate, ProcessResponse

router = APIRouter(prefix="/processes", tags=["processes"])


@router.post("/", response_model=ProcessResponse, status_code=201)
def create_process(data: ProcessCreate, db: Session = Depends(get_db)):
    """
    공정 생성. parent_id 가 있으면 그 부모 공정의 존재를 먼저 검증.
    """
    if data.parent_id is not None:
        parent = db.query(Process).filter(Process.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="부모 공정을 찾을 수 없습니다")

    process = Process(
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
    )
    db.add(process); db.commit(); db.refresh(process)
    return process


@router.get("/", response_model=list[ProcessResponse])
def list_processes(
    parent_id: int | None = Query(default=None, description="미전달 시 최상위만, 값 있으면 그 자식만"),
    db: Session = Depends(get_db),
):
    """
    parent_id 가 None 이면 최상위 공정만 (parent_id IS NULL),
    값이 있으면 그 부모의 직속 자식만.

    SQLAlchemy 의 IS NULL 표현은 '== None' 으로 작성해야 한다.
    """
    query = db.query(Process)
    if parent_id is None:
        query = query.filter(Process.parent_id == None)   # noqa: E711  ← IS NULL
    else:
        query = query.filter(Process.parent_id == parent_id)
    return query.all()


@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(process_id: int, db: Session = Depends(get_db)):
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")
    return process
