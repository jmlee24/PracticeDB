"""day5/complete/routes/categories.py — Day3 와 동일."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day5.complete.database import get_db
from day5.complete.models import Category
from day5.complete.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=data.name, description=data.description, is_active=data.is_active)
    db.add(category); db.commit(); db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(is_active: bool | None = Query(default=None), db: Session = Depends(get_db)):
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
