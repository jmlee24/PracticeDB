"""
day4/complete/routes/products.py — 통합 목록 API (완성형, 줄단위 해설)
================================================================
Day 4 의 핵심. 7개 쿼리 파라미터를 하나의 list_products 에 결합:
    page, size               — 페이지네이션
    search                   — 이름 부분검색 (ilike)
    min_price, max_price     — 가격 범위
    sort_by, order           — 동적 정렬
    category_id              — 카테고리 필터 (Day 2 부터)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.complete.database import get_db
from day4.complete.models import Category, Product
from day4.complete.schemas import ProductCreate, ProductResponse, PaginatedResponse

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
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터)"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 건수"),
    search: str | None = Query(default=None, description="상품 이름 부분검색"),
    min_price: int | None = Query(default=None, ge=0, description="최저 가격"),
    max_price: int | None = Query(default=None, ge=0, description="최고 가격"),
    sort_by: str = Query(default="id", description="정렬 컬럼명 (id/name/price/stock)"),
    order: str = Query(default="asc", description="asc / desc"),
    category_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """통합 목록 — 모든 조건이 누적 적용된다."""
    query = db.query(Product)

    # 1) 필터 누적 (조건이 있을 때만)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if search:
        # ilike: PostgreSQL 의 대소문자 무관 LIKE. '%키워드%' 로 부분검색.
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        # 함정: 'if min_price:' 로 쓰면 0 이 falsy 라 0원 필터가 무시됨.
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # 2) 동적 정렬
    # getattr(Product, "price", None) → Product.price (없으면 None)
    # 잘못된 sort_by 가 와도 None 체크로 안전 (정렬 생략).
    column = getattr(Product, sort_by, None)
    if column is not None:
        query = query.order_by(column.desc() if order == "desc" else column.asc())

    # 3) 전체 건수 — ★반드시 offset/limit 적용 전에★
    total = query.count()

    # 4) 페이지네이션 적용
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()

    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product
