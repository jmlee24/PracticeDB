"""
day4/practice/routes/items.py — list_items 통합 API (TODO 빈칸)
================================================================
[과제] complete/routes/products.py 의 list_products 를 옮긴다.
       단 가격 범위(min_price/max_price) 자리에 재고 범위(min_stock/max_stock) 적용.

매핑:
    complete                practice
    --------                --------
    search                  keyword     (이름 변경)
    min_price/max_price     min_stock/max_stock
    Product.price 비교      Item.stock 비교
    sort_by 컬럼 후보       id/name/price/stock 동일
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.practice.database import get_db
from day4.practice.models import Brand, Item
from day4.practice.schemas import ItemCreate, ItemResponse, PaginatedResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    """완성. Day 2~3 와 동일 패턴."""
    brand = db.query(Brand).filter(Brand.id == data.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다")
    item = Item(
        name=data.name, description=data.description, price=data.price,
        stock=data.stock, brand_id=data.brand_id,
    )
    db.add(item); db.commit(); db.refresh(item)
    return item


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 1] 통합 list_items API                                │
# │                                                            │
# │ Query 파라미터:                                            │
# │ - page: int = Query(default=1, ge=1)                       │
# │ - size: int = Query(default=10, ge=1, le=100)              │
# │ - keyword: str | None = Query(default=None)                │
# │ - min_stock: int | None = Query(default=None, ge=0)        │
# │ - max_stock: int | None = Query(default=None, ge=0)        │
# │ - sort_by: str = Query(default="id")                       │
# │ - order: str = Query(default="asc")                        │
# │ - brand_id: int | None = Query(default=None)               │
# │                                                            │
# │ 본문(complete list_products 패턴):                         │
# │   query = db.query(Item)                                   │
# │   if brand_id is not None: query = query.filter(...)       │
# │   if keyword: query = query.filter(                        │
# │       Item.name.ilike(f"%{keyword}%"))                     │
# │   if min_stock is not None:                                │
# │       query = query.filter(Item.stock >= min_stock)        │
# │   if max_stock is not None:                                │
# │       query = query.filter(Item.stock <= max_stock)        │
# │   column = getattr(Item, sort_by, None)                    │
# │   if column is not None:                                   │
# │       query = query.order_by(column.desc()                 │
# │           if order == "desc" else column.asc())            │
# │   total = query.count()                                    │
# │   offset = (page - 1) * size                               │
# │   items = query.offset(offset).limit(size).all()           │
# │   return PaginatedResponse(                                │
# │       total=total, page=page, size=size, items=items)      │
# │                                                            │
# │ 함정 1: 'if min_stock:' → 0 이 falsy. 반드시 'is not None'. │
# │ 함정 2: count() 를 offset.limit 다음에 호출하면 페이지     │
# │         크기만 셈. 반드시 적용 전!                         │
# └──────────────────────────────────────────────────────────┘


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """완성. 참고용."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return item
