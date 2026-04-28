"""day5/complete/routes/products.py — Day4 의 통합 list_products 그대로."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day5.complete.database import get_db
from day5.complete.models import Category, Product
from day5.complete.schemas import ProductCreate, ProductResponse, PaginatedResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    product = Product(
        name=data.name, description=data.description, price=data.price,
        stock=data.stock, category_id=data.category_id,
    )
    db.add(product); db.commit(); db.refresh(product)
    return product


@router.get("/", response_model=PaginatedResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    sort_by: str = Query(default="id"),
    order: str = Query(default="asc"),
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    column = getattr(Product, sort_by, None)
    if column is not None:
        query = query.order_by(column.desc() if order == "desc" else column.asc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product
