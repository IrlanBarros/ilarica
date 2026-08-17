"""Pytest global fixtures for integration tests.

Provides:
- `engine`, `SessionLocal` to use an in-memory SQLite DB for tests
- `override_get_db` fixture to patch FastAPI dependency
- `client` fixture returning `TestClient(app)`

Notes:
- Tests run against the FastAPI `app` defined in `main.py`.
- Uses SQLAlchemy metadata to create tables in-memory for isolation.
"""
from __future__ import annotations

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.dependencies.auth import get_current_user
from app.domain.access_identity.user import User
from app.database.session import get_db
from app.core.security import get_password_hash
from main import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Use a single connection for in-memory DB so schema persists across sessions
_connection = engine.connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_connection)


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    """Create all tables once per test session on the open connection."""
    Base.metadata.create_all(bind=_connection)
    yield
    Base.metadata.drop_all(bind=_connection)
    _connection.close()


def override_get_db() -> Generator:
    """Yield a SQLAlchemy session for a test and ensure rollback/close."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def mock_current_user() -> User:
    """Return a deterministic authenticated user for protected route tests."""
    return User(
        id="test-auth-user",
        email="qa-auth@ufca.edu.br",
        password_hash=get_password_hash("Secret123"),
        role="admin",
        is_active=True,
    )


@pytest.fixture(autouse=True)
def app_dependency_overrides(mock_current_user: User):
    """Override app dependencies for isolated integration tests."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a direct test DB session for setup/seed steps."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
