"""day3/practice/routes/items.py — Item CRUD (완성, 참고용)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day3.practice.database import get_db
from day3.practice.models import Brand, Item
from day3.practice.schemas import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == data.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    item = Item(
        name=data.name, description=data.description, price=data.price,
        stock=data.stock, brand_id=data.brand_id,
    )
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.get("/", response_model=list[ItemResponse])
def list_items(brand_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Item)
    if brand_id is not None:
        query = query.filter(Item.brand_id == brand_id)
    return query.all()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return item
