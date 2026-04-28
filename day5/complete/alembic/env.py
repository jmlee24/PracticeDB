"""
day5/complete/alembic/env.py — Alembic 환경 설정
================================================================
target_metadata 가 핵심.
이 변수가 가리키는 메타데이터(=Base.metadata) 를 모델 코드의 진실로 간주.
DB 의 현재 상태와 비교해 'autogenerate' 가 차이를 마이그레이션 파일로 만든다.

실행 위치: day5/complete/ 폴더에서.
    cd day5/complete
    alembic revision --autogenerate -m "초기 스키마"
    alembic upgrade head
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# day5.complete.database 을 import 하기 위해 프로젝트 루트(StudyDB/) 를 sys.path 에 추가.
# 이 env.py 는 day5/complete/alembic/ 안에 있으므로, 부모의 부모의 부모 = StudyDB/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from day5.complete.database import Base
from day5.complete import models  # noqa: F401  ← 모델 import → Base.metadata 에 등록

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """오프라인 모드: 실제 DB 연결 없이 SQL 스크립트만 출력."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """온라인 모드: 실제 DB 에 연결해 마이그레이션 실행."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
