"""day7/practice/routes/departments.py — 완성 (Day6 practice 답안 그대로)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day7.practice.database import get_db
from day7.practice.models import Department
from day7.practice.schemas import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    if data.parent_id is not None:
        parent = db.query(Department).filter(Department.id == data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="부모 부서를 찾을 수 없습니다")
    dept = Department(name=data.name, description=data.description, parent_id=data.parent_id)
    db.add(dept); db.commit(); db.refresh(dept)
    return dept


@router.get("/", response_model=list[DepartmentResponse])
def list_departments(parent_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Department)
    if parent_id is None:
        query = query.filter(Department.parent_id == None)  # noqa: E711
    else:
        query = query.filter(Department.parent_id == parent_id)
    return query.all()
