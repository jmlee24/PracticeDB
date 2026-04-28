# Day 1 / practice — Category 노출 토글(is_published) 변형 문제

> 옆 폴더 `day1/complete/` 의 `is_active` 코드를 띄워두고 풀어보세요.
> 같은 패턴, 다른 의미입니다.

## 변형 포인트

| 항목 | complete (참고) | practice (이 폴더) |
|------|-----------------|---------------------|
| 컬럼명 | `is_active` | `is_published` |
| 기본값 | `True` (활성) | **`False`** (비공개) |
| 의미 | 소프트 삭제 플래그 | 콘텐츠 공개 여부 토글 |
| 필터 의도 | 비활성 숨김 | 비공개 숨김 |

## 환경 세팅

```bash
# 트랙 전환 시 DB 초기화 (complete 와 스키마가 다를 수 있으므로)
docker compose down -v && docker compose up -d

# 서버 기동
uvicorn day1.practice.main:app --reload
# 또는 complete 와 동시에 띄우려면:
# uvicorn day1.practice.main:app --reload --port 8001
```

## TODO 5종

| # | 파일 | 무엇을 하는가 | 난이도 |
|---|------|--------------|--------|
| 1 | `models.py` | `is_published` Boolean 컬럼 추가 (default=False) | ★☆☆ |
| 2 | `schemas.py` | `CategoryCreate.is_published: bool = False` | ★☆☆ |
| 3 | `schemas.py` | `CategoryResponse.is_published: bool` | ★☆☆ |
| 4 | `routes/categories.py` | create/update 에서 `is_published` 값 전달 | ★☆☆ |
| 5 | `routes/categories.py` | `GET /categories?is_published=...` 필터 추가 | ★★☆ |

## 학습 포인트

### 1. default 값이 의미를 바꾼다
- complete 의 `is_active` 는 기본 True → "기본은 활성, 비활성화는 명시적".
- practice 의 `is_published` 는 기본 False → "기본은 비공개, 공개는 명시적".

같은 컬럼 타입(Boolean) 이라도 default 가 정책을 결정한다는 것을 체감해보세요.

### 2. `if x is not None` 함정 (TODO 5)
```python
# 잘못된 코드
if is_published:
    query = query.filter(...)
# → is_published=False 일 때 falsy 라서 필터가 안 걸린다 (비공개 조회 불가)

# 올바른 코드
if is_published is not None:
    query = query.filter(...)
```

## 검증 체크리스트

```bash
# 1) 카테고리 생성 (is_published 미전달 → False 로 저장)
curl -s -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "초안", "description": "아직 공개 안함"}' | python -m json.tool
# 기대: is_published=false

# 2) 명시적으로 공개 카테고리 생성
curl -s -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "공개카테고리", "is_published": true}' | python -m json.tool
# 기대: is_published=true

# 3) 공개된 것만 필터링
curl -s "http://localhost:8000/categories/?is_published=true" | python -m json.tool
# 기대: '공개카테고리' 만 나옴

# 4) 비공개만 필터링 (False 도 정상 작동하는지 확인 — 함정 통과)
curl -s "http://localhost:8000/categories/?is_published=false" | python -m json.tool
# 기대: '초안' 만 나옴
```

## 막혔을 때
- 컬럼 추가가 막힘 → `day1/complete/models.py` 의 `is_active` 줄 참고
- 필터 패턴이 막힘 → `day1/complete/routes/categories.py` 의 `list_categories` 참고
- `from_attributes` 가 뭔지 → `day1/complete/schemas.py` 끝 주석 참고
