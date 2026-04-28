"""day7/complete/routes/bom.py"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day7.complete.database import get_db
from day7.complete.models import BOMEntry, Product
from day7.complete.schemas import BOMEntryCreate, BOMEntryResponse

router = APIRouter(prefix="/bom", tags=["bom"])


def _to_response(entry: BOMEntry) -> BOMEntryResponse:
    return BOMEntryResponse(
        id=entry.id, product_id=entry.product_id, material_id=entry.material_id,
        material_name=entry.material.name, quantity=entry.quantity, unit=entry.unit,
    )


@router.post("/", response_model=BOMEntryResponse, status_code=201)
def create_bom(data: BOMEntryCreate, db: Session = Depends(get_db)):
    if data.product_id == data.material_id:
        raise HTTPException(status_code=400, detail="완제품과 자재가 동일할 수 없습니다")
    if not db.query(Product).filter(Product.id == data.product_id).first():
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")
    if not db.query(Product).filter(Product.id == data.material_id).first():
        raise HTTPException(status_code=404, detail="자재를 찾을 수 없습니다")
    entry = BOMEntry(**data.model_dump())
    db.add(entry); db.commit(); db.refresh(entry)
    return _to_response(entry)


@router.get("/product/{product_id}", response_model=list[BOMEntryResponse])
def get_bom(product_id: int, db: Session = Depends(get_db)):
    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()
    return [_to_response(e) for e in entries]
