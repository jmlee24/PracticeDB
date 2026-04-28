"""
day2/complete/routes/categories.py — Category CRUD (Day1과 동일)
================================================================
Day 1 의 categories 라우트와 거의 같다. 차이점: import 경로뿐.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day2.complete.database import get_db
from day2.complete.models import Category
from day2.complete.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=data.name, description=data.description, is_active=data.is_active)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Category)
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    return query.all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    category.name = data.name
    category.description = data.description
    category.is_active = data.is_active
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    db.delete(category)
    db.commit()
