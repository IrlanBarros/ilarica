"""Database session configuration and dependency injection helpers."""

from __future__ import annotations

import os
from collections.abc import Generator
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

db_user = os.getenv("DB_USER", "ilarica_admin")
db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
db_name = os.getenv("DB_NAME", "ilarica_db")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5433")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
