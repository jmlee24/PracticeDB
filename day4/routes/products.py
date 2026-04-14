"""
상품 API 라우트 — Day 4: 페이지네이션 + 검색 + 정렬
=====================================================
Day 3 완성 CRUD 위에 list_products를 단계적으로 개선합니다.

TODO 29~32를 순서대로 풀면서 list_products 하나에 기능을 쌓아가세요.
TODO 34는 29~32를 모두 합친 최종 통합 과제입니다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day4.database import get_db
from day4.models import Product, Category
from day4.schemas import ProductCreate, ProductResponse, PaginatedResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """상품 생성"""
    category = db.query(Category).filter(Category.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
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


# ┌──────────────────────────────────────────────────┐
# │ [TODO 34] 통합 상품 목록 API (★★★)                │
# │                                                    │
# │ TODO 29~32를 하나의 list_products 함수에 합칩니다. │
# │                                                    │
# │ 파라미터 (모두 Query):                             │
# │ - page: int = 1 (ge=1)                             │
# │ - size: int = 10 (ge=1, le=100)                    │
# │ - search: str | None = None  (이름 부분검색)        │
# │ - category_id: int | None = None                   │
# │ - min_price: int | None = None                     │
# │ - max_price: int | None = None                     │
# │ - sort_by: str = "id"                              │
# │ - order: str = "asc"                               │
# │                                                    │
# │ 반환: PaginatedResponse                            │
# │                                                    │
# │ 로직 순서:                                         │
# │ 1. query = db.query(Product)                       │
# │ 2. 필터 적용 (category_id, search, price 범위)     │
# │ 3. 정렬 적용 (sort_by + order)                     │
# │ 4. total = query.count()                           │
# │ 5. offset = (page - 1) * size                      │
# │ 6. items = query.offset(offset).limit(size).all()  │
# │ 7. PaginatedResponse 반환                          │
# └──────────────────────────────────────────────────┘

# ┌──────────────────────────────────────────────────┐
# │ [TODO 29] offset/limit 페이지네이션 (★★☆)         │
# │                                                    │
# │ 기존 list_products에 페이지네이션을 추가하세요.     │
# │                                                    │
# │ 추가 파라미터:                                     │
# │ - page: int = Query(default=1, ge=1)               │
# │ - size: int = Query(default=10, ge=1, le=100)      │
# │                                                    │
# │ 로직:                                              │
# │   offset = (page - 1) * size                       │
# │   total = query.count()                            │
# │   items = query.offset(offset).limit(size).all()   │
# │                                                    │
# │ 반환: PaginatedResponse(                           │
# │     total=total, page=page,                        │
# │     size=size, items=items                         │
# │ )                                                  │
# │                                                    │
# │ TODO 30~32를 이 함수에 순서대로 추가하세요.         │
# └──────────────────────────────────────────────────┘

# ┌──────────────────────────────────────────────────┐
# │ [TODO 30] ilike 이름 검색 (★★☆)                   │
# │                                                    │
# │ TODO 29 완성 후 이 필터를 추가하세요.               │
# │                                                    │
# │ 추가 파라미터:                                     │
# │ - search: str | None = Query(default=None)         │
# │                                                    │
# │ 로직 (query 구성 단계에 삽입):                     │
# │   if search:                                       │
# │       query = query.filter(                        │
# │           Product.name.ilike(f"%{search}%")        │
# │       )                                            │
# │                                                    │
# │ 포인트: ilike는 대소문자를 구분하지 않는 LIKE 검색  │
# │ SQL: WHERE name ILIKE '%저항%'                     │
# └──────────────────────────────────────────────────┘

# ┌──────────────────────────────────────────────────┐
# │ [TODO 31] 가격 범위 필터 (★★☆)                    │
# │                                                    │
# │ TODO 30 완성 후 이 필터를 추가하세요.               │
# │                                                    │
# │ 추가 파라미터:                                     │
# │ - min_price: int | None = Query(default=None)      │
# │ - max_price: int | None = Query(default=None)      │
# │                                                    │
# │ 로직:                                              │
# │   if min_price is not None:                        │
# │       query = query.filter(                        │
# │           Product.price >= min_price               │
# │       )                                            │
# │   if max_price is not None:                        │
# │       query = query.filter(                        │
# │           Product.price <= max_price               │
# │       )                                            │
# └──────────────────────────────────────────────────┘

# ┌──────────────────────────────────────────────────┐
# │ [TODO 32] 동적 정렬 (★★★)                         │
# │                                                    │
# │ TODO 31 완성 후 이 정렬 로직을 추가하세요.          │
# │                                                    │
# │ 추가 파라미터:                                     │
# │ - sort_by: str = Query(default="id")               │
# │ - order: str = Query(default="asc")                │
# │                                                    │
# │ 로직:                                              │
# │   # getattr로 모델 컬럼을 동적으로 가져옴           │
# │   column = getattr(Product, sort_by, None)         │
# │   if column is not None:                           │
# │       if order == "desc":                          │
# │           query = query.order_by(column.desc())    │
# │       else:                                        │
# │           query = query.order_by(column.asc())     │
# │                                                    │
# │ 포인트: getattr(Product, "price", None)은           │
# │ Product.price와 동일 — 문자열로 컬럼을 지정 가능   │
# └──────────────────────────────────────────────────┘
@router.get("/", response_model=PaginatedResponse)
def list_products(
    # TODO 28: ProductSearchParams 스키마 없이 Query 파라미터를 직접 정의
    # → 간단한 검색 조건은 별도 스키마 없이 Query()로 충분
    category_id: int | None = Query(default=None, description="카테고리 ID 필터"),
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
    search: str | None = Query(default=None, description="상품명 부분검색 (대소문자 무관)"),
    min_price: int | None = Query(default=None, description="최소 가격"),
    max_price: int | None = Query(default=None, description="최대 가격"),
    sort_by: str = Query(default="id", description="정렬 기준 컬럼 (id, name, price, stock)"),
    order: str = Query(default="asc", description="정렬 방향 (asc, desc)"),
    db: Session = Depends(get_db),
):
    """상품 목록 조회 — 페이지네이션 + 검색 + 가격 범위 + 동적 정렬"""
    query = db.query(Product)

    # TODO 29: 카테고리 필터 (기존 로직 유지)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    # TODO 30: 이름 부분검색 — ilike는 대소문자 구분 없는 LIKE
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # TODO 31: 가격 범위 필터
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # TODO 32: 동적 정렬 — getattr로 문자열을 컬럼 객체로 변환
    column = getattr(Product, sort_by, None)
    if column is not None:
        if order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # TODO 29: 페이지네이션 — count()는 필터 적용 후 전체 건수
    total = query.count()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()

    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """상품 단건 조회"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductCreate, db: Session = Depends(get_db)):
    """상품 수정"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
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
    """상품 삭제"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    db.delete(product)
    db.commit()
