import pytest
from unittest.mock import MagicMock
from app.modules.auth.services import (
    create_user,
    authenticate_user,
    create_access_token,
    decode_access_token,
    create_refresh_token
)
from app.database.models import User
from jose import jwt
from app.config import settings


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.mark.asyncio
async def test_create_user(mock_db):
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    email = "test@example.com"
    password = "securepassword"
    role = "admin"

    user = await create_user(mock_db, email, password, role)

    assert user.email == email
    assert user.role == role
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_success(mock_db):
    fake_user = User(id=1,
                     email="test@example.com",
                     hashed_password="$2b$12$KIX"
                     )
    mock_db.query().filter().first.return_value = fake_user

    from app.modules.auth import services
    services.pwd_context.verify = lambda pwd, hash: True

    user = await authenticate_user(mock_db, "test@example.com", "password")
    assert user == fake_user


@pytest.mark.asyncio
async def test_authenticate_user_fail_no_user(mock_db):
    mock_db.query().filter().first.return_value = None
    user = await authenticate_user(mock_db, "fake@example.com", "password")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_fail_bad_password(mock_db):
    fake_user = User(id=1, email="test@example.com", hashed_password="wrong")
    mock_db.query().filter().first.return_value = fake_user

    from app.modules.auth import services
    services.pwd_context.verify = lambda pwd, hash: False

    user = await authenticate_user(mock_db, "test@example.com", "badpassword")
    assert user is None


def test_create_access_token():
    data = {"sub": "test@example.com", "role": "admin"}
    token = create_access_token(data)
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "admin"


def test_decode_access_token_valid():
    data = {"sub": "test@example.com", "role": "admin"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"


def test_decode_access_token_invalid():
    bad_token = "invalid.token.value"
    result = decode_access_token(bad_token)
    assert result is None


def test_create_refresh_token():
    data = {"sub": "user@example.com"}
    token = create_refresh_token(data)
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    assert decoded["sub"] == "user@example.com"
