"""
day2/practice/routes/items.py — Item CRUD + FK 검증 (TODO 빈칸)
================================================================
[과제] complete/routes/products.py 의 패턴을 Item 에 적용.

TODO 6~11: 5개 핸들러를 Brand FK 검증 포함해 완성한다.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day2.practice.database import get_db
from day2.practice.models import Brand, Item
from day2.practice.schemas import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 6] 상품 생성 (POST /items/)                          │
# │                                                            │
# │ 조건:                                                      │
# │ - 1. brand_id 존재 검증 → 없으면 404                       │
# │ - 2. Item(...) 생성, db.add, commit, refresh, return       │
# │                                                            │
# │ 힌트(complete 의 create_product 패턴):                     │
# │   brand = db.query(Brand).filter(Brand.id == ...).first()  │
# │   if not brand: raise HTTPException(404, ...)              │
# │   item = Item(name=..., price=..., brand_id=...)           │
# │   db.add(item); db.commit(); db.refresh(item); return item │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 7] 상품 목록 (GET /items/, brand_id 필터)            │
# │                                                            │
# │ 힌트(complete 의 list_products 패턴):                      │
# │   brand_id: int | None = Query(default=None)               │
# │   query = db.query(Item)                                   │
# │   if brand_id is not None: query = query.filter(...)       │
# │   return query.all()                                       │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 8] 상품 단건 조회 (GET /items/{item_id})             │
# │                                                            │
# │ 힌트: complete 의 get_product 와 완전히 동일               │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 9] 상품 수정 (PUT /items/{item_id})                  │
# │                                                            │
# │ 조건:                                                      │
# │ - 1. 기존 Item 조회 → 없으면 404                           │
# │ - 2. 새 brand_id 도 검증 → 없으면 404                      │
# │ - 3. 모든 필드 갱신 후 commit                              │
# │                                                            │
# │ 힌트: complete 의 update_product 패턴                      │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 10] 상품 삭제 (DELETE /items/{item_id})              │
# │                                                            │
# │ 힌트: complete 의 delete_product 와 동일                   │
# └──────────────────────────────────────────────────────────┘
