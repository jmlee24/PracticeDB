"""day7/practice/routes/items.py — 완성"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day7.practice.database import get_db
from day7.practice.models import Brand, Item
from day7.practice.schemas import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    if not db.query(Brand).filter(Brand.id == data.brand_id).first():
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    item = Item(**data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.get("/", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return item
