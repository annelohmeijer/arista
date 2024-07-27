import os
from functools import lru_cache

from alembic import command
from alembic.config import Config
from sqlmodel import Session, SQLModel, create_engine


@lru_cache
def get_engine():
    """Get a cached database engine."""
    postgres_url = os.enviorn.get("POSTGRES_DATABASE_URL")
    if postgres_url is None:
        raise ValueError("POSTGRES_DATABASE_URL not set.")
    return create_engine(postgres_url)


def init_db():
    """Setup db and create tables"""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def run_migrations():
    """Run migrations with Alembic"""
    alembic_cfg = Config("alemibic.ini")
    command.upgrade(alembic_cfg, "head")


def get_session() -> Session:
    """Get a database session.

    Args:
        engine: SQLModel engine."""
    engine = get_engine()
    session = Session(bind=engine, autocommit=False, autoflush=False)
    try:
        yield session
    finally:
        session.close()
