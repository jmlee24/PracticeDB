"""
day6/practice/routes/departments.py — Department CRUD (TODO 빈칸)
================================================================
[과제] complete/routes/processes.py 의 패턴을 Department 로 옮긴다.
       parent_id 검증 + IS NULL 필터링까지 동일.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day6.practice.database import get_db
# from day6.practice.models import Department                    # ← TODO 1 완성 후 활성
# from day6.practice.schemas import DepartmentCreate, DepartmentResponse  # ← TODO 3,4 완성 후

router = APIRouter(prefix="/departments", tags=["departments"])


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 7] POST /departments/                                │
# │                                                            │
# │ 흐름(complete create_process 패턴):                        │
# │   if data.parent_id is not None:                           │
# │       parent = db.query(Department).filter(...).first()    │
# │       if not parent: raise HTTPException(404)              │
# │   dept = Department(name=..., parent_id=...)               │
# │   db.add(dept); db.commit(); db.refresh(dept); return dept │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 8] GET /departments/?parent_id=...                   │
# │                                                            │
# │ - parent_id is None → 최상위만 (parent_id == None 필터)    │
# │ - parent_id 있으면 → 그 자식만                             │
# │                                                            │
# │ 힌트: complete list_processes 그대로                       │
# │ 함정: SQLAlchemy 의 IS NULL 은 'col == None' 으로 작성.    │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 9] GET /departments/{department_id}                  │
# │ 힌트: complete get_process 패턴                            │
# └──────────────────────────────────────────────────────────┘
