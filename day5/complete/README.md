# Day 5 / complete — Alembic 마이그레이션 + 인덱스 완성 참고

## 학습 목표
- `Base.metadata.create_all` 대신 **Alembic** 으로 스키마 변경 이력 관리
- `index=True`, `Index()`, `UniqueConstraint()` 활용
- `__table_args__` 튜플 패턴

## 신규 코드 위치

| 무엇 | 파일 | 라인 |
|------|------|------|
| `index=True` (단일 인덱스) | `models.py` | `Product.name`, `Order.status` |
| `Index("이름", "c1", "c2")` | `models.py` | `Order.__table_args__` |
| `UniqueConstraint(...)` | `models.py` | `Product.__table_args__` |
| `target_metadata = Base.metadata` | `alembic/env.py` | autogenerate 의 진실 원본 |
| `create_all` 제거 | `main.py` | 주석 처리됨 |

## 실행 절차 (반드시 이 순서)

```bash
# 1) DB 초기화
docker compose down -v && docker compose up -d

# 2) day5/complete 폴더로 이동
cd day5/complete

# 3) 첫 마이그레이션 자동 생성
alembic revision --autogenerate -m "초기 스키마"

# 4) 적용
alembic upgrade head

# 5) 다른 터미널에서 서버 기동 (StudyDB 루트로 돌아가서)
cd ../..
uvicorn day5.complete.main:app --reload
```

## Alembic 한 줄 워크플로

```bash
# 모델 변경 후 한 줄로 끝
alembic revision --autogenerate -m "변경 설명" && alembic upgrade head

# 한 단계 롤백
alembic downgrade -1

# 모든 이력 보기
alembic history --verbose

# 현재 적용된 revision
alembic current
```

## 핵심 주의

- `--autogenerate` 가 **감지 못하는** 변경: 데이터 변환, 시퀀스, 일부 server_default. 이런 건 `alembic revision -m "..."` 로 빈 파일 만들어 직접 작성.
- `op.add_column / op.drop_column / op.create_index` 등 op.* 함수가 마이그레이션 파일에 들어간다.
