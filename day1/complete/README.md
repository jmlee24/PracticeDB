# Day 1 / complete — Category CRUD 완성 참고

## 학습 목표
이 폴더는 **읽기·참고용**입니다. 모든 코드가 채워져 있고, 줄단위 한국어 주석으로
"이 한 줄이 SQL로 어떻게 변환되는가"를 설명합니다. 옆 폴더 `day1/practice/`의
TODO를 풀 때 이 코드를 띄워두고 참고하세요.

## 만들어지는 DB 구조

```
categories
┌────────────┬──────────────┬──────────┐
│ 컬럼        │ 타입          │ 제약      │
├────────────┼──────────────┼──────────┤
│ id          │ INTEGER       │ PK       │
│ name        │ VARCHAR(100)  │ NOT NULL UNIQUE │
│ description │ TEXT          │ NULL OK  │
│ is_active   │ BOOLEAN       │ NOT NULL DEFAULT True │
│ created_at  │ TIMESTAMP     │ INSERT 시 UTC now │
└────────────┴──────────────┴──────────┘

INDEX ix_categories_id ON categories(id)
```

## 엔드포인트 5종

| 메서드 | 경로 | 설명 | 학습 포인트 |
|--------|------|------|-------------|
| POST | `/categories/` | 생성 | `db.add → commit → refresh` 3단계 |
| GET  | `/categories/` | 목록 (is_active 필터) | `if x is not None` 으로 False 살리기 |
| GET  | `/categories/{id}` | 단건 | `.first()` + 404 패턴 |
| PUT  | `/categories/{id}` | 수정 | dirty tracking — 속성 할당만으로 UPDATE |
| DELETE | `/categories/{id}` | 삭제 | 204 No Content |

## 실행

```bash
# 1) PostgreSQL 기동 (이미 떠 있으면 스킵)
docker compose up -d

# 2) 서버 기동 (StudyDB 루트에서)
uvicorn day1.complete.main:app --reload

# 3) Swagger UI
# http://localhost:8000/docs

# 4) 헬스체크 — DB 연결까지 검증
curl http://localhost:8000/health
# → {"status":"ok","db":"connected"}
```

## 핵심 라인 인덱스

| 무엇을 보고 싶은가 | 파일 | 줄 위치 |
|-----------------|------|---------|
| `Base = declarative_base()` 가 만드는 것 | database.py | 끝부분 |
| Column 6종이 SQL로 어떻게 변환되는가 | models.py | Category 클래스 본문 |
| `from_attributes=True` 의 역할 | schemas.py | CategoryResponse 끝줄 |
| `Depends(get_db)` 가 자동으로 close 하는 흐름 | database.py | get_db 함수 |
| `if is_active is not None:` 함정 | routes/categories.py | list_categories |
| `db.commit()` 후 `db.refresh()` 가 필요한 이유 | routes/categories.py | create_category |

## 다음 단계
이 코드를 충분히 이해했다면 `day1/practice/` 로 가서 살짝 다른 변형 문제(`is_published`)를 풀어보세요.
