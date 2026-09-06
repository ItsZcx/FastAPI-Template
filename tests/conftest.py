import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.database import Base
from src.core.database import get_db
from src.core.rate_limit import limiter
from src.main import app

TEST_DB_URL = os.getenv("TEST_DB_URL", "postgresql://postgres:1234@localhost:5432/postgres_test")
ADMIN_DB_URL = os.getenv("DB_URL", "postgresql://postgres:1234@localhost:5432/postgres")


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Create the test database once per test session."""
    admin_engine = create_engine(ADMIN_DB_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        exists = connection.execute(text("SELECT 1 FROM pg_database WHERE datname = 'postgres_test'")).scalar()
        if not exists:
            connection.execute(text("CREATE DATABASE postgres_test"))
    admin_engine.dispose()
    yield


@pytest.fixture(scope="session")
def engine(create_test_database):
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db(engine):
    """Session joined to an outer transaction; rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield
