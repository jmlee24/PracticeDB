"""
day6/complete/routes/bom.py — BOM CRUD + 비용 집계 (완성형, 줄단위 해설)
================================================================
핵심: BOMEntryResponse 의 material_name 은 모델 필드가 아니다.
      relationship(material) 로 가져온 후 라우트에서 명시 주입한다.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day6.complete.database import get_db
from day6.complete.models import BOMEntry, Product
from day6.complete.schemas import BOMEntryCreate, BOMEntryResponse

router = APIRouter(prefix="/bom", tags=["bom"])


def _to_response(entry: BOMEntry) -> BOMEntryResponse:
    """ORM BOMEntry → BOMEntryResponse. material_name 을 수동 주입."""
    return BOMEntryResponse(
        id=entry.id,
        product_id=entry.product_id,
        material_id=entry.material_id,
        material_name=entry.material.name,   # ← relationship 으로 끌어옴
        quantity=entry.quantity,
        unit=entry.unit,
    )


@router.post("/", response_model=BOMEntryResponse, status_code=201)
def create_bom_entry(data: BOMEntryCreate, db: Session = Depends(get_db)):
    """완제품/자재 둘 다 검증 + 자기 자신 자재 금지."""
    if data.product_id == data.material_id:
        raise HTTPException(status_code=400, detail="완제품과 자재가 동일할 수 없습니다")

    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")
    material = db.query(Product).filter(Product.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="자재를 찾을 수 없습니다")

    entry = BOMEntry(
        product_id=data.product_id,
        material_id=data.material_id,
        quantity=data.quantity,
        unit=data.unit,
    )
    db.add(entry); db.commit(); db.refresh(entry)
    return _to_response(entry)


@router.get("/product/{product_id}", response_model=list[BOMEntryResponse])
def get_bom_by_product(product_id: int, db: Session = Depends(get_db)):
    """제품별 자재 명세서."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()
    return [_to_response(e) for e in entries]


@router.get("/product/{product_id}/cost")
def get_bom_cost(product_id: int, db: Session = Depends(get_db)):
    """완제품 1개를 만드는 데 드는 자재 총 비용."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")

    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()
    items = []
    total_cost = 0.0
    for e in entries:
        subtotal = e.material.price * e.quantity
        total_cost += subtotal
        items.append({
            "material_name": e.material.name,
            "quantity": e.quantity,
            "unit": e.unit,
            "unit_price": e.material.price,
            "subtotal": subtotal,
        })

    return {
        "product_id": product.id,
        "product_name": product.name,
        "total_cost": total_cost,
        "items": items,
    }
