# Day 4 / complete — 페이지네이션 + 검색 + 정렬 완성 참고

## 학습 목표
하나의 `list_products` 엔드포인트에 **7개 쿼리 파라미터**를 결합한 실무형 목록 API 패턴.

## 7가지 쿼리 파라미터

| 파라미터 | 타입 | 의미 |
|---------|------|------|
| `page` | int (≥1) | 페이지 번호 |
| `size` | int (1~100) | 페이지당 건수 |
| `search` | str? | 이름 부분검색 (ilike, 대소문자 무관) |
| `min_price` | int? | 최저 가격 |
| `max_price` | int? | 최고 가격 |
| `sort_by` | str | 정렬 컬럼명 (id/name/price/stock) |
| `order` | "asc"/"desc" | 정렬 방향 |
| `category_id` | int? | 카테고리 필터 |

## 핵심 패턴 4가지

1. **필터 누적**: `query = query.filter(...)` 를 조건부로 쌓기.
2. **`if x is not None`** : `0` 도 유효한 값이라 falsy 체크 금지.
3. **`getattr` 동적 정렬**: 문자열 → 컬럼 객체. 잘못된 이름은 `None` 으로 안전.
4. **`count()` 위치**: `offset/limit` **이전** — 그래야 전체 건수가 나온다.

## 검증 curl

```bash
docker compose down -v && docker compose up -d
uvicorn day4.complete.main:app --reload

# 기본 페이지네이션
curl "http://localhost:8000/products/?page=1&size=5"

# 검색 + 가격 범위 + 정렬
curl "http://localhost:8000/products/?search=저항&min_price=30&max_price=200&sort_by=price&order=desc"

# 응답 구조: {total, page, size, items: [...]}
```
