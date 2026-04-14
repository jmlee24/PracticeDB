"""
BOM(자재명세서) API 라우트 — Day 6 완성본
==========================================
완제품 1개를 만들기 위해 필요한 자재 목록(BOM)을 관리합니다.
Dual FK 패턴: product_id(완제품)와 material_id(자재) 모두 products 테이블 참조.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day7.database import get_db
from day7.models import BOMEntry, Product
from day7.schemas import BOMEntryCreate, BOMEntryResponse

router = APIRouter(prefix="/bom", tags=["bom"])


@router.post("/", response_model=BOMEntryResponse, status_code=201)
def create_bom_entry(data: BOMEntryCreate, db: Session = Depends(get_db)):
    """BOM 항목 생성"""
    # 완제품 존재 확인
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")

    # 자재 존재 확인
    material = db.query(Product).filter(Product.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="자재를 찾을 수 없습니다")

    # 완제품과 자재가 동일한 경우 방지
    if data.product_id == data.material_id:
        raise HTTPException(status_code=400, detail="완제품과 자재는 동일할 수 없습니다")

    entry = BOMEntry(
        product_id=data.product_id,
        material_id=data.material_id,
        quantity=data.quantity,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/", response_model=list[BOMEntryResponse])
def list_bom_entries(
    product_id: int | None = None,
    db: Session = Depends(get_db),
):
    """BOM 목록 조회 — product_id로 특정 완제품의 BOM만 필터 가능"""
    query = db.query(BOMEntry)
    if product_id is not None:
        query = query.filter(BOMEntry.product_id == product_id)
    return query.all()


@router.get("/{entry_id}", response_model=BOMEntryResponse)
def get_bom_entry(entry_id: int, db: Session = Depends(get_db)):
    """BOM 항목 단건 조회"""
    entry = db.query(BOMEntry).filter(BOMEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="BOM 항목을 찾을 수 없습니다")
    return entry


@router.put("/{entry_id}", response_model=BOMEntryResponse)
def update_bom_entry(entry_id: int, data: BOMEntryCreate, db: Session = Depends(get_db)):
    """BOM 항목 수정"""
    entry = db.query(BOMEntry).filter(BOMEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="BOM 항목을 찾을 수 없습니다")
    entry.product_id = data.product_id
    entry.material_id = data.material_id
    entry.quantity = data.quantity
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_bom_entry(entry_id: int, db: Session = Depends(get_db)):
    """BOM 항목 삭제"""
    entry = db.query(BOMEntry).filter(BOMEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="BOM 항목을 찾을 수 없습니다")
    db.delete(entry)
    db.commit()
