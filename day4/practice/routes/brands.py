"""day4/practice/routes/brands.py — Brand CRUD (완성, 참고용)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.practice.database import get_db
from day4.practice.models import Brand
from day4.practice.schemas import BrandCreate, BrandResponse

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("/", response_model=BrandResponse, status_code=201)
def create_brand(data: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(name=data.name, description=data.description, is_active=data.is_active)
    db.add(brand); db.commit(); db.refresh(brand)
    return brand


@router.get("/", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).all()


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    return brand
