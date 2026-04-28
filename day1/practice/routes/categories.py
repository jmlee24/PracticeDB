"""
day1/practice/routes/categories.py — Category CRUD (TODO 빈칸 문제)
==================================================================
[과제] complete 의 is_active 필터를 is_published 필터로 바꿔 적용한다.
       create/update 핸들러도 is_published 필드를 ORM 객체에 전달해야 한다.

참고: day1/complete/routes/categories.py 의 list_categories 함수가
      'if is_active is not None: ... filter ...' 패턴을 보여준다.
      여기서는 is_active 자리에 is_published 를 넣으면 된다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day1.practice.database import get_db
from day1.practice.models import Category
from day1.practice.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """카테고리 생성."""
    category = Category(
        name=data.name,
        description=data.description,
        # ┌────────────────────────────────────────────────┐
        # │ [TODO 4] is_published 값 전달                   │
        # │                                                  │
        # │ 힌트: is_published=data.is_published            │
        # │      (complete 의 is_active=data.is_active 패턴)│
        # └────────────────────────────────────────────────┘
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    # ┌──────────────────────────────────────────────────────┐
    # │ [TODO 5] is_published 쿼리 파라미터 추가              │
    # │                                                        │
    # │ 조건:                                                  │
    # │ - 파라미터: is_published: bool | None = Query(default=None) │
    # │ - is_published 가 None 이 아니면 그 값으로 필터링      │
    # │                                                        │
    # │ 힌트(complete 패턴):                                   │
    # │   query = db.query(Category)                           │
    # │   if is_published is not None:                         │
    # │       query = query.filter(                            │
    # │           Category.is_published == is_published)       │
    # │   return query.all()                                   │
    # │                                                        │
    # │ 함정: 'if is_published:' 로 쓰면 False 가 falsy 라     │
    # │       비공개 필터링이 안된다. 반드시 'is not None'.    │
    # └──────────────────────────────────────────────────────┘
    db: Session = Depends(get_db),
):
    """카테고리 목록 — is_published 필터 적용."""
    return db.query(Category).all()  # ← TODO 5 완성 시 여기를 query 변수 패턴으로 교체


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """단건 조회. complete 와 동일 — 그대로 둔다."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    """수정 — is_published 도 갱신해야 한다."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    category.name = data.name
    category.description = data.description
    # ┌────────────────────────────────────────────────┐
    # │ [TODO 4-2] is_published 갱신                    │
    # │ category.is_published = data.is_published      │
    # └────────────────────────────────────────────────┘

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """삭제. complete 와 동일."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    db.delete(category)
    db.commit()
