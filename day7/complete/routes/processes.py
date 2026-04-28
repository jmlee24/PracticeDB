"""day7/complete/routes/processes.py"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day7.complete.database import get_db
from day7.complete.models import Process
from day7.complete.schemas import ProcessCreate, ProcessResponse

router = APIRouter(prefix="/processes", tags=["processes"])


@router.post("/", response_model=ProcessResponse, status_code=201)
def create_process(data: ProcessCreate, db: Session = Depends(get_db)):
    if data.parent_id is not None:
        parent = db.query(Process).filter(Process.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="부모 공정을 찾을 수 없습니다")
    process = Process(name=data.name, description=data.description, parent_id=data.parent_id)
    db.add(process); db.commit(); db.refresh(process)
    return process


@router.get("/", response_model=list[ProcessResponse])
def list_processes(parent_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Process)
    if parent_id is None:
        query = query.filter(Process.parent_id == None)  # noqa: E711
    else:
        query = query.filter(Process.parent_id == parent_id)
    return query.all()
