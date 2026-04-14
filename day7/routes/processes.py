"""
공정 API 라우트 — Day 6 완성본
================================
자기참조 계층(트리) 구조를 가진 공정(Process) CRUD입니다.
parent_id를 통해 공정 간 상하위 관계를 표현합니다.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day7.database import get_db
from day7.models import Process
from day7.schemas import ProcessCreate, ProcessResponse

router = APIRouter(prefix="/processes", tags=["processes"])


@router.post("/", response_model=ProcessResponse, status_code=201)
def create_process(data: ProcessCreate, db: Session = Depends(get_db)):
    """공정 생성"""
    # 부모 공정이 지정된 경우 존재 여부 확인
    if data.parent_id is not None:
        parent = db.query(Process).filter(Process.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="상위 공정을 찾을 수 없습니다")

    process = Process(
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
    )
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


@router.get("/", response_model=list[ProcessResponse])
def list_processes(db: Session = Depends(get_db)):
    """공정 전체 목록 조회"""
    return db.query(Process).all()


@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(process_id: int, db: Session = Depends(get_db)):
    """공정 단건 조회"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")
    return process


@router.put("/{process_id}", response_model=ProcessResponse)
def update_process(process_id: int, data: ProcessCreate, db: Session = Depends(get_db)):
    """공정 수정"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")

    # 자기 자신을 부모로 설정하는 순환 참조 방지
    if data.parent_id == process_id:
        raise HTTPException(status_code=400, detail="공정은 자기 자신을 상위 공정으로 설정할 수 없습니다")

    if data.parent_id is not None:
        parent = db.query(Process).filter(Process.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="상위 공정을 찾을 수 없습니다")

    process.name = data.name
    process.description = data.description
    process.parent_id = data.parent_id
    db.commit()
    db.refresh(process)
    return process


@router.delete("/{process_id}", status_code=204)
def delete_process(process_id: int, db: Session = Depends(get_db)):
    """공정 삭제"""
    process = db.query(Process).filter(Process.id == process_id).first()
    if not process:
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")
    db.delete(process)
    db.commit()
