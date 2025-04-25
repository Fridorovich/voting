import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.modules.voting.routes import router
from app.modules.voting.services import get_active_polls
from unittest.mock import AsyncMock

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_get_all_active_polls(client, monkeypatch):
    mock_polls = [{
        "id": 1,
        "title": "Test Poll",
        "description": "Test Description",
        "close_date": "2023-01-01T00:00:00",
        "is_closed": True,
        "results": {"Option 1": 2, "Option 2": 1}
    }]
    
    mock_service = AsyncMock(return_value=mock_polls)
    monkeypatch.setattr("app.modules.voting.routes.get_active_polls", mock_service)
    
    response = client.get("/polls/")
    
    assert response.status_code == 200
    assert response.json() == mock_polls
    mock_service.assert_awaited_once()