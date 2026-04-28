"""
day5/practice/routes/items.py — Item CRUD + 페이지네이션 (완성, 참고용)
================================================================
이 파일은 완성되어 있다. TODO 는 schemas/models 측에만 있고,
라우트는 그대로 동작하도록 둔다.

단, ItemCreate 에 barcode 필드를 추가한 뒤(TODO 6) 여기 create_item 도
'barcode=data.barcode' 한 줄을 추가해야 실제로 저장된다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day5.practice.database import get_db
from day5.practice.models import Brand, Item
from day5.practice.schemas import ItemCreate, ItemResponse, PaginatedResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == data.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    item = Item(
        name=data.name, description=data.description, price=data.price,
        stock=data.stock, brand_id=data.brand_id,
        # ┌────────────────────────────────────────────────┐
        # │ [TODO 8] barcode=data.barcode 추가               │
        # │ TODO 6 (schemas) 와 짝. ItemCreate.barcode 가    │
        # │ 정의된 후 이 줄을 풀어 실제 저장.               │
        # └────────────────────────────────────────────────┘
    )
    db.add(item); db.commit(); db.refresh(item)
    return item


@router.get("/", response_model=PaginatedResponse)
def list_items(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = Query(default=None),
    min_stock: int | None = Query(default=None, ge=0),
    max_stock: int | None = Query(default=None, ge=0),
    sort_by: str = Query(default="id"),
    order: str = Query(default="asc"),
    brand_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Day4 practice 의 통합 list_items — 완성본."""
    query = db.query(Item)
    if brand_id is not None:
        query = query.filter(Item.brand_id == brand_id)
    if keyword:
        query = query.filter(Item.name.ilike(f"%{keyword}%"))
    if min_stock is not None:
        query = query.filter(Item.stock >= min_stock)
    if max_stock is not None:
        query = query.filter(Item.stock <= max_stock)
    column = getattr(Item, sort_by, None)
    if column is not None:
        query = query.order_by(column.desc() if order == "desc" else column.asc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return item
