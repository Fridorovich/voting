from fastapi.testclient import TestClient


def test_get_all_polls(client: TestClient):
    response = client.get("/polls/")
    assert response.status_code == 200
    assert response.json() == []
