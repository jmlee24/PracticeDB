"""day7/practice/routes/brands.py — 완성"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day7.practice.database import get_db
from day7.practice.models import Brand
from day7.practice.schemas import BrandCreate, BrandResponse

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("/", response_model=BrandResponse, status_code=201)
def create_brand(data: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(name=data.name, description=data.description, is_active=data.is_active)
    db.add(brand); db.commit(); db.refresh(brand)
    return brand


@router.get("/", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).all()
