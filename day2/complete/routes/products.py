"""
day2/complete/routes/products.py — Product CRUD + FK 검증 (완성형)
================================================================
Day 1 의 categories 패턴 + "FK 사전 검증" 한 단계 추가.

FK 사전 검증을 왜 하나?
    DB에 IntegrityError 만 맡겨도 동작은 하지만, FastAPI 응답이 500 으로 나가서
    "어떤 카테고리가 없다" 라는 정보를 클라이언트가 알 수 없다.
    create/update 시점에 직접 카테고리 존재 확인 → 명확한 404 반환.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day2.complete.database import get_db
from day2.complete.models import Category, Product
from day2.complete.schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """상품 생성 — category_id 가 실재하는지 먼저 확인."""
    # Step 1: FK 사전 검증
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    # Step 2: 상품 객체 생성 + 저장
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=list[ProductResponse])
def list_products(
    category_id: int | None = Query(default=None, description="카테고리 ID 필터"),
    db: Session = Depends(get_db),
):
    """상품 목록 — category_id 쿼리 파라미터로 카테고리별 필터링."""
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


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductCreate, db: Session = Depends(get_db)):
    """수정 — 새 category_id 도 FK 검증 필요 (카테고리 변경 가능하므로)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # 카테고리 변경 시 새 ID 도 검증
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    product.name = data.name
    product.description = data.description
    product.price = data.price
    product.stock = data.stock
    product.category_id = data.category_id
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    db.delete(product)
    db.commit()
