import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import get_db, SessionLocal
from app.database.models import User
from app.modules.auth.services import pwd_context
import jwt
from datetime import datetime, timedelta
from app.config import settings

client = TestClient(app)


# Override dependency
@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def override_get_db(db):
    def _get_test_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture(scope="function")
def test_user(db, unique_email):
    password = "securepassword"
    hashed = pwd_context.hash(password)
    user = User(
        email=unique_email,
        hashed_password=hashed,
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user.raw_password = password
    return user


def test_register_user_success(db, override_get_db):
    email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "newpassword123"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert pwd_context.verify(password, user.hashed_password)


def test_register_user_existing(
        test_user,
        override_get_db
):
    response = client.post(
        "/auth/register",
        json={"email": test_user.email, "password": "irrelevant"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(test_user, override_get_db):
    response = client.post(
        "/auth/login",
        json={"email": test_user.email,
              "password": test_user.raw_password}
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_invalid_password(test_user, override_get_db):
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_nonexistent_user(override_get_db):
    response = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "nope"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_token_refresh(test_user, override_get_db):
    refresh_payload = {
        "sub": test_user.email,
        "role": test_user.role
    }
    expire = datetime.now() + timedelta(days=7)
    refresh_payload.update({"exp": expire})

    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    response = client.post(
        "/auth/token/refresh",
        params={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["token_type"] == "bearer"


def test_token_refresh_invalid(override_get_db):
    response = client.post(
        "/auth/token/refresh",
        params={"refresh_token": "invalid.token.value"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_logout(override_get_db):
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}
