"""
day1/complete/routes/categories.py — Category CRUD 라우트 (완성형, 줄단위 해설)
==============================================================================
HTTP 메서드 → CRUD 매핑:
    POST   /categories         → CREATE (생성)
    GET    /categories         → READ  (목록, is_active 필터)
    GET    /categories/{id}    → READ  (단건)
    PUT    /categories/{id}    → UPDATE (전체 수정)
    DELETE /categories/{id}    → DELETE (삭제)

각 핸들러는 Depends(get_db) 로 주입된 세션 1개를 사용한다.
요청 끝나면 get_db 의 finally 가 자동으로 close.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from day1.complete.database import get_db
from day1.complete.models import Category
from day1.complete.schemas import CategoryCreate, CategoryResponse

# APIRouter: 라우트 묶음. main.py 의 include_router 로 앱에 붙인다.
# prefix="/categories" → 아래 모든 경로 앞에 자동으로 붙음.
# tags=["categories"] → Swagger UI 에서 그룹 라벨로 사용.
router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """
    카테고리 생성. 성공 시 201 Created.

    흐름:
        1) Pydantic 이 data 를 검증 (실패 시 422 자동)
        2) ORM 객체 생성 (아직 DB 반영 안 됨, 메모리만)
        3) db.add() → INSERT 대기열에 넣음
        4) db.commit() → 실제 INSERT 실행 + 트랜잭션 확정
        5) db.refresh() → DB가 만든 id, created_at 등을 객체에 다시 채워넣음
    """
    category = Category(
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    db.add(category)         # 트랜잭션의 INSERT 대기열에 추가
    db.commit()              # COMMIT → 영구 반영
    db.refresh(category)     # DB가 채운 id, created_at 동기화
    return category          # CategoryResponse 로 자동 직렬화 (from_attributes=True 덕분)


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    is_active: bool | None = Query(default=None, description="활성 여부로 필터링. 미전달 시 전체."),
    db: Session = Depends(get_db),
):
    """
    카테고리 목록 조회. is_active 쿼리 파라미터로 활성/비활성 필터.

        GET /categories                 → 전체
        GET /categories?is_active=true  → 활성만 (소프트 삭제 안된 것)
        GET /categories?is_active=false → 비활성만 (소프트 삭제된 것)

    핵심 패턴: query 변수에 조건을 누적해서 마지막에 .all() 호출.
              if is_active is not None: 으로 None 과 False 를 명확히 구분 (False 는 falsy 값이므로).
    """
    query = db.query(Category)
    if is_active is not None:                                # is_active=False 도 살리기 위해 'is not None'
        query = query.filter(Category.is_active == is_active) # WHERE is_active = ?
    return query.all()                                       # SELECT * FROM categories [WHERE ...]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    카테고리 단건 조회. 없으면 404.

    .first() 는 결과가 없으면 None 을 반환 (예외 안 던짐).
    None 체크 후 직접 HTTPException 을 던져 404 를 만든다.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    """
    카테고리 전체 수정 (PUT 의 의미상 모든 필드 갱신).

    흐름:
        1) 대상 조회 → 없으면 404
        2) 객체 속성에 값 할당 (이 시점엔 메모리만 변경)
        3) db.commit() → SQLAlchemy 가 변경 감지해 UPDATE 실행
        4) db.refresh() → updated_at 등 DB가 갱신한 값 재로딩
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    # 변경 감지(dirty tracking) — 객체 속성을 바꾸면 SQLAlchemy 가 알아서 UPDATE 를 만든다.
    category.name = data.name
    category.description = data.description
    category.is_active = data.is_active

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    카테고리 하드 삭제. 성공 시 204 No Content (응답 본문 없음).

    참고: 실무에서는 is_active=False 로 두는 "소프트 삭제" 가 더 안전하다.
          이 엔드포인트는 학습용으로 진짜 DELETE 를 보여준다.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    db.delete(category)   # DELETE 대기열에 추가
    db.commit()           # 실제 DELETE 실행
