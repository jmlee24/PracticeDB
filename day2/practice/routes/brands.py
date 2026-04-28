"""
day2/practice/routes/brands.py — Brand CRUD (완성, 참고용)
================================================================
이 파일은 완성되어 있다. Day 1 categories 와 동일한 패턴.
이걸 참고해 items.py 의 TODO를 풀 수 있다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day2.practice.database import get_db
from day2.practice.models import Brand
from day2.practice.schemas import BrandCreate, BrandResponse

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("/", response_model=BrandResponse, status_code=201)
def create_brand(data: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(name=data.name, description=data.description, is_active=data.is_active)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.get("/", response_model=list[BrandResponse])
def list_brands(
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Brand)
    if is_active is not None:
        query = query.filter(Brand.is_active == is_active)
    return query.all()


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    return brand


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(brand_id: int, data: BrandCreate, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    brand.name = data.name
    brand.description = data.description
    brand.is_active = data.is_active
    db.commit()
    db.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=204)
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    db.delete(brand)
    db.commit()
