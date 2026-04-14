# StudyDB - 7일 DB + 백엔드 연동 워크북

FastAPI + PostgreSQL + SQLAlchemy로 배우는 실무 DB 설계 & API 개발 연습 프로젝트.

각 Day 폴더의 완성된 참고 코드를 읽고, TODO 주석을 찾아 빈칸을 채우는 **워크북 스타일**입니다.

---

## 전체 로드맵

| Day | 테마 | TODO | 난이도 | 핵심 개념 |
|-----|------|------|--------|----------|
| 1 | CRUD 기초 읽기 + 수정 | 1~5 (5개) | ★☆☆ | ORM 매핑, Session, 스키마 분리 |
| 2 | 상품 + 외래키(FK) | 6~16 (11개) | ★☆☆~★★☆ | ForeignKey, relationship |
| 3 | 주문 + 트랜잭션 | 17~26 (10개) | ★★☆~★★★ | 트랜잭션, rollback, nested JSON |
| 4 | 페이지네이션 + 검색 + 정렬 | 27~34 (8개) | ★★☆ | offset/limit, ilike, 동적 정렬 |
| 5 | Alembic 마이그레이션 + 인덱스 | 35~41 (7개) | ★★☆ | 마이그레이션 CLI, 인덱스, B-Tree |
| 6 | MES: 공정 + BOM | 42~53 (12개) | ★★☆~★★★ | 자기참조 FK, M:N, 자재명세서 |
| 7 | MES: 작업지시 + 상태머신 | 54~65 (10+2보너스) | ★★★ | 상태 전이, BOM 연동, 복합 트랜잭션 |

총 **63개 본문 TODO + 2개 보너스** = 65개

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

# 4. Day 1 서버 실행 (StudyDB 폴더에서)
uvicorn day1.main:app --reload
```

실행 후 http://localhost:8000/docs 에서 Swagger UI로 API를 테스트할 수 있습니다.

---

## Day 전환 시 DB 초기화

각 Day는 독립적인 앱입니다. Day를 전환할 때는 DB를 초기화하세요:

```bash
# 1. 이전 Day 서버 종료 (Ctrl+C)

# 2. DB 초기화 (데이터 + 테이블 모두 삭제 후 재생성)
docker compose down -v && docker compose up -d

# 3. 새 Day 서버 실행
uvicorn day2.main:app --reload
```

> Day 5부터는 Alembic을 사용하므로 `alembic upgrade head`를 먼저 실행해야 합니다.

---

## 풀이 방법

1. **exercises.md 먼저 읽기**: 각 Day 폴더의 `exercises.md`가 학습 가이드입니다
2. **완성 코드 참고**: 같은 파일 내의 완성된 부분이나 이전 Day의 코드를 참고하세요
3. **TODO 순서대로**: 모델 → 스키마 → 라우트 순서로 풀어야 합니다
4. **Swagger로 검증**: http://localhost:8000/docs 에서 직접 API를 호출해 확인하세요

---

## 프로젝트 구조

```
StudyDB/
├── README.md              ← 지금 읽고 있는 파일
├── docker-compose.yml     ← PostgreSQL 컨테이너
├── requirements.txt       ← Python 패키지 목록
├── day1/                  ← CRUD 기초
├── day2/                  ← 상품 + FK
├── day3/                  ← 주문 + 트랜잭션
├── day4/                  ← 페이지네이션 + 검색
├── day5/                  ← Alembic + 인덱스
├── day6/                  ← MES: 공정 + BOM
├── day7/                  ← MES: 작업지시
└── phase1/                ← 초기 연습 코드 (참고용)
```

---

## 트러블슈팅

### Docker가 실행되지 않을 때
```bash
# Docker Desktop이 실행 중인지 확인
docker info

# 포트 5432가 이미 사용 중이면
# docker-compose.yml에서 포트를 변경: "5433:5432"
# 그리고 각 Day의 database.py에서 URL도 변경
```

### psycopg2 설치 실패
```bash
# Windows에서 빌드 오류 시
pip install psycopg2-binary  # binary 버전 사용 (이미 requirements.txt에 포함)
```

### 서버 실행 시 ModuleNotFoundError
```bash
# StudyDB 폴더(최상위)에서 실행해야 합니다
cd /path/to/StudyDB
uvicorn day1.main:app --reload  # day1 폴더 안에서 실행하면 안 됨!
```

### 포트 8000이 이미 사용 중
```bash
# 다른 Day의 서버가 실행 중이면 먼저 종료 (Ctrl+C)
# 또는 다른 포트로 실행
uvicorn day1.main:app --reload --port 8001
```

### Alembic 관련 오류 (Day 5+)
```bash
# DB 초기화 후 마이그레이션 적용
docker compose down -v && docker compose up -d
cd day5
alembic upgrade head
```
