from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from alembic import context
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("One or more environment variables for the database connection are not set")

# 데이터베이스 URL 생성
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Alembic 설정
config = context.config
# `sqlalchemy.url`은 설정하지 않음

Base = declarative_base()

# SQLAlchemy 모델의 메타데이터 설정
target_metadata = Base.metadata

def run_migrations_online():
    # DATABASE_URL을 사용하여 엔진 생성
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

def run_migrations_offline():
    # 이 경우에는 DATABASE_URL을 사용할 수 없습니다.
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()