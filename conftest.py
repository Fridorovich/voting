# conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.database.base import Base
from app.database.session import get_db


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./sqr_voting.db"


@pytest.fixture(scope="module")
def engine():
    return create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope="module")
def db_engine(engine):
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session  # это и есть наш db

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db: Session):
    def override_get_db():
        yield db  # передаем тестовую сессию

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def mock_user():
    return {"email": "user@example.com"}
