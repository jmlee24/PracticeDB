# StudyDB - 7일 DB + 백엔드 연동 워크북 (듀얼 트랙)

FastAPI + PostgreSQL + SQLAlchemy 로 배우는 DB 설계 & API 개발 연습 프로젝트.

각 Day 가 두 개의 트랙으로 분리되어 있습니다:

| 트랙 | 폴더 | 역할 |
|------|------|------|
| **complete** | `dayN/complete/` | 모든 코드가 채워진 완성형. 줄단위 한국어 주석. **읽기·참고용.** |
| **practice** | `dayN/practice/` | complete 를 살짝 변형한 빈칸 문제. **보고 푸는 용.** |

학습 흐름: complete 를 띄워두고 practice 의 TODO 를 채우면서, 같은 패턴이 어떻게 다른 도메인에 적용되는지 체감합니다.

---

## 전체 로드맵

| Day | 주제 | complete (참고) | practice (변형 문제) |
|-----|------|----------------|--------------------|
| 1 | CRUD 기초 | Category + `is_active` (소프트 삭제) | Category + `is_published` (노출 토글, default 반대) |
| 2 | 외래키 + 관계 | Category 1:N Product | Brand 1:N Item |
| 3 | 트랜잭션 | Order/OrderItem (재고 차감) | Booking/BookingSeat (좌석 예약) |
| 4 | 페이지/검색/정렬 | list_products + 가격 범위 | list_items + 재고 범위 |
| 5 | Alembic + 인덱스 | Index/UQ(name, category_id) | barcode 추가 + UQ(name, brand_id) |
| 6 | 자기참조 + Dual FK | Process 트리 + BOM | Department 트리 + Recipe |
| 7 | 상태머신 | WorkOrder (4 상태) | Shipment (5 상태, **HOLD 추가**) |

---

## 환경 세팅

### 필수 프로그램
- Python 3.11+
- Docker Desktop
- Git

### 설치 & 실행

```bash
# 1. PostgreSQL 실행
docker compose up -d

# 2. 가상환경 생성 & 활성화
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
# source venv/bin/activate     # Mac/Linux

# 3. 패키지 설치
pip install -r requirements.txt

# 4. Day 1 complete 서버 실행 (StudyDB 루트에서!)
uvicorn day1.complete.main:app --reload
# 또는 practice:
uvicorn day1.practice.main:app --reload --port 8001
```

실행 후 http://localhost:8000/docs (또는 :8001) 에서 Swagger UI 로 API 테스트.

---

## 학습 흐름 (권장)

각 Day 마다 다음 순서를 반복합니다:

1. **`dayN/complete/README.md`** 를 먼저 읽기 — 이 Day 가 만드는 DB 구조 + 핵심 라인 인덱스
2. **complete 코드 통째로 읽기** — `models.py` → `schemas.py` → `routes/*.py` 순. 줄단위 주석을 따라가며 SQL 매핑을 머리에 그린다.
3. **complete 서버 띄워서 Swagger 로 클릭** — 실제 동작을 본다.
4. **`dayN/practice/exercises.md`** 의 TODO 목록 확인.
5. **practice 코드의 TODO 채우기** — 막히면 complete 의 같은 위치 참고.
6. **practice 서버 띄워서 검증 curl 실행**.

---

## 트랙 전환 시 DB 초기화

complete ↔ practice 를 오갈 때, 또는 다른 Day 로 넘어갈 때:

```bash
# 1. 이전 서버 종료 (Ctrl+C)

# 2. DB 완전 초기화 (테이블 + 데이터 모두 삭제 후 재생성)
docker compose down -v && docker compose up -d

# 3. 새 트랙 서버 실행
uvicorn day2.complete.main:app --reload
```

> **Day 5 부터는 Alembic** 을 쓰므로 `cd dayN/complete && alembic upgrade head` 가 필요합니다 (자세한 건 `day5/complete/README.md`).

---

## 프로젝트 구조

```
StudyDB/
├── README.md                      ← 지금 읽는 파일
├── COMMANDS.md                    ← 명령어 사전 (모르는 명령은 Ctrl+F)
├── docker-compose.yml             ← PostgreSQL 컨테이너
├── requirements.txt               ← Python 패키지
├── day1/
│   ├── complete/                  ← Category + is_active 완성 + 줄단위 주석
│   │   ├── README.md
│   │   ├── database.py / models.py / schemas.py / main.py
│   │   └── routes/categories.py
│   └── practice/                  ← Category + is_published TODO + exercises.md
│       ├── exercises.md
│       └── (동일 구조)
├── day2/                          ← Category 1:N Product / Brand 1:N Item
├── day3/                          ← Order 트랜잭션 / Booking 좌석예약
├── day4/                          ← 페이지/검색/정렬 통합 API
├── day5/                          ← Alembic + 인덱스 / barcode 변형
│   └── complete/
│       └── alembic/               ← Alembic 환경 (각 트랙별)
├── day6/                          ← Process 자기참조 + BOM / Department + Recipe
├── day7/                          ← WorkOrder 상태머신 / Shipment + HOLD
└── .old/                          ← 듀얼 트랙 분리 전 원본 (참고 보관)
```

---

## 트러블슈팅

### Docker 가 실행되지 않을 때
```bash
docker info                       # Docker Desktop 살아있는지
# 포트 5432 점유 시 docker-compose.yml + database.py 의 5432→5433 변경
```

### `ModuleNotFoundError` (`day1/` 안에서 uvicorn 실행했을 때)
```bash
# 반드시 StudyDB 루트에서 실행:
cd /path/to/StudyDB
uvicorn day1.complete.main:app --reload
```

### 포트 8000 점유 (complete 와 practice 동시 띄우기)
```bash
uvicorn day1.complete.main:app --reload                  # 8000
uvicorn day1.practice.main:app --reload --port 8001       # 8001
```

### Day 5+ Alembic 오류
```bash
docker compose down -v && docker compose up -d
cd day5/complete   # 또는 day5/practice
alembic upgrade head
```

---

## 명령어 사전

모르는 명령어/함수가 나오면 **`COMMANDS.md`** 를 `Ctrl+F` 로 검색하세요. 12개 카테고리(Docker, Alembic, SQLAlchemy 모델/세션, FastAPI, Pydantic, …)로 정리되어 있습니다.
