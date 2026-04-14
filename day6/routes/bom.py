"""
BOM API 라우트 — Day 6 신규
==============================
MES 도메인: 자재명세서(BOM) CRUD + 비용 계산.
Product 테이블을 완제품/자재 양쪽으로 재활용합니다.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from day6.database import get_db
from day6.models import Product, BOMEntry
from day6.schemas import BOMEntryCreate, BOMEntryResponse

router = APIRouter(prefix="/bom", tags=["bom"])


# ┌──────────────────────────────────────────────────┐
# │ [TODO 51] POST / — BOM 항목 등록 (★★☆)           │
# │                                                    │
# │ 검증 순서:                                         │
# │ 1. product_id가 Products 테이블에 존재하는지 확인  │
# │    → 없으면 404                                    │
# │ 2. material_id가 Products 테이블에 존재하는지 확인 │
# │    → 없으면 404                                    │
# │ 3. product_id == material_id이면 400               │
# │    → 완제품 자체를 자재로 사용할 수 없음           │
# │ 4. BOMEntry 생성 후 저장                           │
# └──────────────────────────────────────────────────┘
@router.post("/", response_model=BOMEntryResponse, status_code=201)
def create_bom_entry(data: BOMEntryCreate, db: Session = Depends(get_db)):
    """BOM 항목 등록 — 완제품/자재 존재 확인 + 자기 참조 방지"""
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="완제품을 찾을 수 없습니다")

    material = db.query(Product).filter(Product.id == data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="자재를 찾을 수 없습니다")

    if data.product_id == data.material_id:
        # 순환 참조 방지 — 완제품이 자기 자신을 자재로 가질 수 없음
        raise HTTPException(status_code=400, detail="완제품과 자재가 동일할 수 없습니다")

    entry = BOMEntry(
        product_id=data.product_id,
        material_id=data.material_id,
        quantity=data.quantity,
        unit=data.unit,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # material relationship을 통해 자재 이름을 응답에 포함
    return BOMEntryResponse(
        id=entry.id,
        product_id=entry.product_id,
        material_id=entry.material_id,
        material_name=entry.material.name,
        quantity=entry.quantity,
        unit=entry.unit,
    )


# ┌──────────────────────────────────────────────────┐
# │ [TODO 52] GET /product/{product_id}              │
# │           제품별 BOM 조회 (★★★)                  │
# │                                                    │
# │ 로직:                                              │
# │ 1. product_id 존재 확인 → 없으면 404              │
# │ 2. BOMEntry.product_id == product_id 필터         │
# │ 3. 각 항목에서 entry.material.name을 꺼내          │
# │    BOMEntryResponse 직접 생성                      │
# │                                                    │
# │ material_name이 스키마에 있지만 ORM에는 없으므로   │
# │ from_attributes 직렬화가 아닌 수동 생성 필요.      │
# └──────────────────────────────────────────────────┘
@router.get("/product/{product_id}", response_model=list[BOMEntryResponse])
def get_bom_by_product(product_id: int, db: Session = Depends(get_db)):
    """제품별 BOM 조회 — 해당 완제품에 필요한 자재 목록 반환"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")

    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()

    # material relationship을 통해 자재 이름을 수동으로 주입
    return [
        BOMEntryResponse(
            id=entry.id,
            product_id=entry.product_id,
            material_id=entry.material_id,
            material_name=entry.material.name,
            quantity=entry.quantity,
            unit=entry.unit,
        )
        for entry in entries
    ]


# ┌──────────────────────────────────────────────────┐
# │ [TODO 53] GET /product/{product_id}/cost         │
# │           총 자재 비용 계산 (★★★)                │
# │                                                    │
# │ 로직:                                              │
# │ 1. product_id 존재 확인 → 없으면 404              │
# │ 2. BOM 항목별로 quantity * material.price 합산    │
# │ 3. 응답 형식:                                      │
# │    {                                               │
# │      "product_id": 1,                              │
# │      "product_name": "PCB 보드 A타입",             │
# │      "total_cost": 12500,                          │
# │      "items": [                                    │
# │        {                                           │
# │          "material_name": "저항 10K",              │
# │          "quantity": 10,                           │
# │          "unit": "ea",                             │
# │          "unit_price": 50,                         │
# │          "subtotal": 500                           │
# │        }, ...                                      │
# │      ]                                             │
# │    }                                               │
# └──────────────────────────────────────────────────┘
@router.get("/product/{product_id}/cost")
def get_bom_cost(product_id: int, db: Session = Depends(get_db)):
    """총 자재 비용 계산 — BOM 항목별 수량 × 단가 합산"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")

    entries = db.query(BOMEntry).filter(BOMEntry.product_id == product_id).all()

    items = []
    total_cost = 0.0
    for entry in entries:
        # 자재 단가 × 소요 수량 = 항목별 소계
        subtotal = entry.material.price * entry.quantity
        total_cost += subtotal
        items.append({
            "material_name": entry.material.name,
            "quantity": entry.quantity,
            "unit": entry.unit,
            "unit_price": entry.material.price,
            "subtotal": subtotal,
        })

    return {
        "product_id": product.id,
        "product_name": product.name,
        "total_cost": total_cost,
        "items": items,
    }
