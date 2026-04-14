"""
카테고리 API 라우트 (완성 - 참고용)
====================================
이 파일은 CRUD 패턴의 완성된 예시입니다.
products.py의 TODO를 풀 때 이 파일을 참고하세요.

CRUD란?
- Create: POST   /categories      → 새 카테고리 생성
- Read:   GET    /categories      → 카테고리 목록 조회 (is_active 필터 포함)
- Read:   GET    /categories/{id} → 카테고리 단건 조회
- Update: PUT    /categories/{id} → 카테고리 수정
- Delete: DELETE /categories/{id} → 카테고리 삭제
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day2.database import get_db
from day2.models import Category
from day2.schemas import CategoryCreate, CategoryResponse

router = APIRouter(
    prefix="/categories",  # 모든 경로 앞에 /categories가 붙음
    tags=["categories"],   # Swagger 문서에서 그룹핑용
)


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """
    카테고리 생성

    흐름:
    1. Pydantic 스키마(data)에서 값을 꺼내 ORM 객체 생성
    2. DB 세션에 추가 (add)
    3. 커밋 (commit) → 실제 DB에 반영
    4. refresh → DB가 생성한 값(id, created_at)을 객체에 반영
    """
    category = Category(
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    카테고리 목록 조회

    is_active 파라미터로 활성/비활성 필터링 가능:
    - GET /categories           → 전체 목록
    - GET /categories?is_active=true  → 활성 카테고리만
    - GET /categories?is_active=false → 비활성 카테고리만
    """
    query = db.query(Category)
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    return query.all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    카테고리 단건 조회

    없는 ID로 요청하면 404 에러를 반환합니다.
    이 패턴(조회 → 없으면 404)은 거의 모든 단건 조회에서 사용됩니다.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
):
    """
    카테고리 수정

    흐름:
    1. 기존 데이터 조회 (없으면 404)
    2. 필드 값 업데이트
    3. 커밋
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    category.name = data.name
    category.description = data.description
    category.is_active = data.is_active
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    카테고리 삭제

    status_code=204: "성공했지만 응답 본문 없음" (삭제의 관례)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    db.delete(category)
    db.commit()
