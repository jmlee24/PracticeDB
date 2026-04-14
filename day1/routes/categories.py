"""
카테고리 API 라우트 (완성 + TODO 1개)
======================================
CRUD 패턴을 읽고 이해한 뒤, TODO 5를 풀어보세요.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from day1.database import get_db
from day1.models import Category
from day1.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """카테고리 생성"""
    category = Category(
        name=data.name,
        description=data.description,
        # is_active=data.is_active,  # TODO 2~4 완성 후 이 줄의 주석을 해제하세요
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    # ┌──────────────────────────────────────────────────┐
    # │ [TODO 5] is_active 필터 파라미터 추가              │
    # │                                                    │
    # │ 조건:                                              │
    # │ - 파라미터: is_active: bool | None = Query(        │
    # │     default=None)                                  │
    # │ - is_active가 None이 아니면 해당 값으로 필터링     │
    # │                                                    │
    # │ 힌트:                                              │
    # │   1. 함수 시그니처에 is_active 파라미터 추가       │
    # │   2. 함수 본문에서:                                │
    # │      query = db.query(Category)                    │
    # │      if is_active is not None:                     │
    # │          query = query.filter(                     │
    # │              Category.is_active == is_active)      │
    # │      return query.all()                            │
    # │                                                    │
    # │ 참고: Day 2의 products.py에서도 같은 패턴을       │
    # │ 사용하게 됩니다. 여기서 연습해두세요!              │
    # └──────────────────────────────────────────────────┘
    db: Session = Depends(get_db),
):
    """카테고리 목록 조회"""
    return db.query(Category).all()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """카테고리 단건 조회"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    """카테고리 수정"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    category.name = data.name
    category.description = data.description
    # category.is_active = data.is_active  # TODO 2~4 완성 후 이 줄의 주석을 해제하세요
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """카테고리 삭제"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    db.delete(category)
    db.commit()
