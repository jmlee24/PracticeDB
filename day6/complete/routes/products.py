"""day6/complete/routes/products.py — Day2 와 동일."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day6.complete.database import get_db
from day6.complete.models import Category, Product
from day6.complete.schemas import ProductCreate, ProductResponse

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


@router.get("/", response_model=list[ProductResponse])
def list_products(category_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    return query.all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product
