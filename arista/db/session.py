import os
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, SQLModel, create_engine


@lru_cache
def get_async_engine():
    """Get a cached aysync database engine."""
    postgres_url = os.environ.get("POSTGRES_DATABASE_URL")
    if postgres_url is None:
        raise ValueError("POSTGRES_DATABASE_URL not set.")
    return create_async_engine(postgres_url, echo=True)


@lru_cache
def get_engine():
    """Get a cached database engine."""
    postgres_url = os.environ.get("POSTGRES_DATABASE_URL")
    if postgres_url is None:
        raise ValueError("POSTGRES_DATABASE_URL not set.")
    return create_engine(postgres_url)


def get_async_session() -> AsyncSession:
    """Get an asynchronous database session."""
    engine = get_async_engine()
    async_session = AsyncSession(bind=engine, expire_on_commit=False)
    
    return async_session


def get_session() -> Session:
    """Get a database session.

    Args:
        engine: SQLModel engine."""
    engine = get_engine()
    session = Session(bind=engine, autocommit=False, autoflush=False)
    return session
