"""day7/complete/routes/categories.py"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day7.complete.database import get_db
from day7.complete.models import Category
from day7.complete.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=data.name, description=data.description, is_active=data.is_active)
    db.add(category); db.commit(); db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()
