import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
from app.database.models import User
import uuid

client = TestClient(app)

def generate_unique_email():
    """Generate a unique email for each test run"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture(scope="function")
def unique_email():
    """Fixture to provide a unique email for each test"""
    return generate_unique_email()

@pytest.fixture
def mock_user():
    return User(id=1, email="user@example.com", hashed_password="hashed", role="admin", is_active=True)

@patch("app.modules.auth.routes.get_db")
def test_register_success(mock_get_db, unique_email):
    db = MagicMock()
    db.query().filter().first.return_value = None
    mock_get_db.return_value = db
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()

    payload = {"email": unique_email, "password": "123456"}
    response = client.post("/auth/register", json=payload)
    existing_user = db.query(User).filter(User.email == payload["email"]).first()
    if existing_user:
        return {"detail": "User already exists."}, 400

    assert response.status_code == 200
    assert "message" in response.json()

@patch("app.modules.auth.routes.get_db")
def test_register_existing_user(mock_get_db):
    db = MagicMock()
    db.query().filter().first.return_value = User()
    mock_get_db.return_value = db

    payload = {"email": "existing@example.com", "password": "123456"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400

@patch("app.modules.auth.routes.get_db")
@patch("app.modules.auth.routes.authenticate_user")
@patch("app.modules.auth.routes.create_access_token")
@patch("app.modules.auth.routes.create_refresh_token")
def test_login_success(mock_create_refresh, mock_create_access, mock_authenticate, mock_get_db, mock_user):
    db = MagicMock()
    mock_get_db.return_value = db
    mock_authenticate.return_value = mock_user
    mock_create_access.return_value = "access.token"
    mock_create_refresh.return_value = "refresh.token"

    payload = {"email": mock_user.email, "password": "123456"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

@patch("app.modules.auth.routes.get_db")
@patch("app.modules.auth.routes.authenticate_user")
def test_login_fail(mock_authenticate, mock_get_db):
    db = MagicMock()
    mock_get_db.return_value = db
    mock_authenticate.return_value = None

    payload = {"email": "bad@example.com", "password": "wrong"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
