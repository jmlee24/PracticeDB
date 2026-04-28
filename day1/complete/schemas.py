"""
day1/complete/schemas.py — Pydantic 스키마 (완성형, 줄단위 해설)
================================================================
Pydantic 스키마는 "API 의 입출력 모양" 을 정의한다.
DB 모델(SQLAlchemy)과 분리하는 이유:
    클라이언트가 보내는 데이터(Create) ≠ DB에 저장된 형태 ≠ 클라이언트가 받는 데이터(Response)

예: id/created_at 은 서버가 만드므로 Create 에는 없지만 Response 에는 있다.
"""
from pydantic import BaseModel
from datetime import datetime


class CategoryCreate(BaseModel):
    """
    POST /categories 의 요청 본문 스키마.

    클라이언트가 JSON 으로 보내는 필드만 정의한다.
    - id, created_at 은 서버가 생성하므로 여기에 없음.
    - is_active 의 기본값 True → 미전달 시 활성으로 생성.
    """
    name: str                          # 필수. 누락 시 422 Unprocessable Entity.
    description: str | None = None     # 선택. 누락 시 None (DB에서 NULL).
    is_active: bool = True             # 기본값 True. 클라이언트가 생략해도 활성.


class CategoryResponse(BaseModel):
    """
    GET / POST /categories 의 응답 스키마.

    DB의 모든 컬럼을 클라이언트에 그대로 노출한다.
    Response 에는 기본값을 둘 필요가 없다 — DB에서 읽은 값을 그대로 반환하므로.
    """
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime

    # from_attributes=True 가 핵심.
    # 이 설정이 있어야 Pydantic 이 ORM 객체(Category 인스턴스)의 .id, .name, ...
    # 속성을 자동으로 끄집어내서 응답으로 변환한다.
    # 없으면 dict() 로 일일이 변환해야 한다.
    model_config = {"from_attributes": True}
