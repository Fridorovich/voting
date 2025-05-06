from fastapi.testclient import TestClient


def test_get_all_polls(client: TestClient):
    response = client.get("/polls/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_poll(client: TestClient):
    payload = {
        "title": "Test Poll",
        "description": "string",
        "choices": ["Yes", "No"],
        "is_multiple_choice": False,
        "close_date": "2025-05-06T13:01:00.435Z"
    }
    response = client.post("/polls/polls?token=fake_token", json=payload)
    assert response.status_code == 200
    assert "id" in response.json()


def test_get_poll_details(client: TestClient):
    create_response = client.post(
        "/polls/polls?token=fake_token",
        json={
            "title": "Details Test",
            "choices": ["Yes", "No"],
            "token": "fake_token"
        }
    )
    poll_id = create_response.json()["id"]

    response = client.get(f"/polls/{poll_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Details Test"
