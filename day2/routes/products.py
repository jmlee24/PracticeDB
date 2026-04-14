"""
상품 API 라우트 (TODO 12~16)
==============================
categories.py를 참고해서 상품 CRUD API를 완성하세요.

엔드포인트 목록:
- POST   /products          → 상품 생성 (FK 검증 포함)
- GET    /products          → 상품 목록 조회 (카테고리별 필터링)
- GET    /products/{id}     → 상품 단건 조회
- PUT    /products/{id}     → 상품 수정 (FK 검증 + 업데이트)
- DELETE /products/{id}     → 상품 삭제
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day2.database import get_db
from day2.models import Product, Category
from day2.schemas import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 12] 상품 생성 API                        ★★☆       │
# │                                                            │
# │ - 메서드: POST "/"                                         │
# │ - response_model: ProductResponse                          │
# │ - status_code: 201                                         │
# │                                                            │
# │ 로직:                                                      │
# │ 1. category_id로 카테고리가 존재하는지 먼저 확인           │
# │    → 없으면 HTTPException(404, "카테고리를 찾을 수 없습니다") │
# │ 2. Product 객체 생성 (name, description, price,            │
# │    stock, category_id)                                     │
# │ 3. db.add → db.commit → db.refresh                        │
# │ 4. return product                                          │
# │                                                            │
# │ 힌트: categories.py의 create_category를 참고하되,         │
# │       FK 유효성 검사가 추가된 버전입니다.                  │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 13] 상품 목록 조회 API                   ★★☆       │
# │                                                            │
# │ - 메서드: GET "/"                                          │
# │ - response_model: list[ProductResponse]                    │
# │                                                            │
# │ 로직:                                                      │
# │ 1. 기본 쿼리: db.query(Product)                            │
# │ 2. category_id 파라미터가 있으면 해당 카테고리만 필터링    │
# │ 3. .all()로 결과 반환                                      │
# │                                                            │
# │ 함수 시그니처:                                             │
# │   def list_products(                                       │
# │       category_id: int | None = Query(default=None),       │
# │       db: Session = Depends(get_db),                       │
# │   ):                                                       │
# │                                                            │
# │ 힌트:                                                      │
# │   query = db.query(Product)                                │
# │   if category_id is not None:                              │
# │       query = query.filter(Product.??? == ???)              │
# │   return query.all()                                       │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 14] 상품 단건 조회 API                   ★☆☆       │
# │                                                            │
# │ - 메서드: GET "/{product_id}"                              │
# │ - response_model: ProductResponse                          │
# │                                                            │
# │ 로직:                                                      │
# │ 1. product_id로 조회                                       │
# │ 2. 없으면 404                                              │
# │ 3. 있으면 반환                                             │
# │                                                            │
# │ 힌트: categories.py의 get_category와 동일한 패턴          │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 15] 상품 수정 API                        ★★★       │
# │                                                            │
# │ - 메서드: PUT "/{product_id}"                              │
# │ - response_model: ProductResponse                          │
# │                                                            │
# │ 로직:                                                      │
# │ 1. product_id로 기존 상품 조회 (없으면 404)                │
# │ 2. category_id 유효성 검사 (없는 카테고리면 404)           │
# │ 3. 모든 필드 업데이트:                                     │
# │    product.name = data.name                                │
# │    product.description = data.description                  │
# │    product.price = data.price                              │
# │    product.stock = data.stock                              │
# │    product.category_id = data.category_id                  │
# │ 4. db.commit → db.refresh → return                        │
# │                                                            │
# │ 힌트: TODO 12의 FK 검사 + update 패턴 조합                │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 16] 상품 삭제 API                        ★☆☆       │
# │                                                            │
# │ - 메서드: DELETE "/{product_id}"                           │
# │ - status_code: 204                                         │
# │                                                            │
# │ 힌트: categories.py의 delete_category와 동일한 패턴       │
# └──────────────────────────────────────────────────────────┘
