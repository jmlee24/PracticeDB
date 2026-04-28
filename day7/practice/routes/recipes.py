"""day7/practice/routes/recipes.py — 완성"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day7.practice.database import get_db
from day7.practice.models import Recipe, Item
from day7.practice.schemas import RecipeCreate, RecipeResponse

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _to_response(r: Recipe) -> RecipeResponse:
    return RecipeResponse(
        id=r.id, product_id=r.product_id, material_id=r.material_id,
        material_name=r.material.name, quantity=r.quantity, unit=r.unit,
    )


@router.post("/", response_model=RecipeResponse, status_code=201)
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)):
    if data.product_id == data.material_id:
        raise HTTPException(status_code=400, detail="제품과 자재가 동일할 수 없습니다")
    if not db.query(Item).filter(Item.id == data.product_id).first():
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
    if not db.query(Item).filter(Item.id == data.material_id).first():
        raise HTTPException(status_code=404, detail="자재를 찾을 수 없습니다")
    r = Recipe(**data.model_dump())
    db.add(r); db.commit(); db.refresh(r)
    return _to_response(r)


@router.get("/product/{product_id}", response_model=list[RecipeResponse])
def get_recipes(product_id: int, db: Session = Depends(get_db)):
    rs = db.query(Recipe).filter(Recipe.product_id == product_id).all()
    return [_to_response(r) for r in rs]
