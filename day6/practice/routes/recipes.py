"""
day6/practice/routes/recipes.py — Recipe CRUD + 비용 집계 (TODO 빈칸)
================================================================
[과제] complete/routes/bom.py 의 패턴을 Recipe 로 옮긴다.
       material_name 수동 주입까지 동일하다.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day6.practice.database import get_db
# from day6.practice.models import Recipe, Item                  # ← TODO 2 완성 후 활성
# from day6.practice.schemas import RecipeCreate, RecipeResponse # ← TODO 5,6 완성 후

router = APIRouter(prefix="/recipes", tags=["recipes"])


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 10] POST /recipes/                                   │
# │                                                            │
# │ 흐름(complete create_bom_entry 패턴):                      │
# │   if data.product_id == data.material_id:                  │
# │       raise HTTPException(400, "동일 불가")                │
# │   product = db.query(Item).filter(...).first()             │
# │   if not product: raise HTTPException(404, "완제품 없음")  │
# │   material = db.query(Item).filter(...).first()            │
# │   if not material: raise HTTPException(404, "자재 없음")   │
# │   recipe = Recipe(product_id=..., material_id=...,         │
# │                   quantity=..., unit=...)                  │
# │   db.add(recipe); db.commit(); db.refresh(recipe)          │
# │   return RecipeResponse(                                   │
# │       id=recipe.id, product_id=...,                        │
# │       material_id=..., material_name=recipe.material.name, │
# │       quantity=..., unit=...,                              │
# │   )                                                        │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 11] GET /recipes/product/{product_id}                │
# │                                                            │
# │ 흐름(complete get_bom_by_product):                         │
# │   product 검증 → entries = db.query(Recipe).filter(...)    │
# │   list comprehension 으로 RecipeResponse 변환              │
# │   (material_name=e.material.name 주입)                     │
# └──────────────────────────────────────────────────────────┘


# ┌──────────────────────────────────────────────────────────┐
# │ [TODO 12] GET /recipes/product/{product_id}/cost           │
# │                                                            │
# │ 자재 총 비용 = Σ (e.material.price * e.quantity)           │
# │                                                            │
# │ 힌트: complete get_bom_cost 그대로                         │
# └──────────────────────────────────────────────────────────┘
