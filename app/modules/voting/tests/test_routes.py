# app/modules/voting/tests/test_routes.py
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest


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


def test_vote_in_poll(client: TestClient, mock_user):
    # 1. Создаем опрос
    create_response = client.post(
        "/polls/polls?token=fake_token",
        json={
            "title": "Vote Test",
            "choices": ["Yes", "No"],
            "token": "fake_token"
        }
    )
    assert create_response.status_code == 200
    poll_id = create_response.json()["id"]

    # 2. Голосуем
    vote_payload = {
        "choice_ids": [1]
    }

    with patch("app.shared.security.get_current_user", return_value=mock_user):
        vote_response = client.post(
            f"/polls/{poll_id}/vote?token=fake_token",
            json=vote_payload
        )

    assert vote_response.status_code == 200
    assert vote_response.json() == {"message": "Vote successful"}


def test_get_poll_details(client: TestClient):
    # Создаем опрос
    create_response = client.post(
        "/polls/polls?token=fake_token",
        json={
            "title": "Test Poll for GET",
            "description": "This poll should return data",
            "choices": ["Option A", "Option B"],
            "is_multiple_choice": False,
            "close_date": "2025-05-06T13:01:00.435Z"
        }
    )
    assert create_response.status_code == 200
    poll_id = create_response.json()["id"]

    # Запрашиваем детали
    response = client.get(f"/polls/{poll_id}")
    assert response.status_code == 200

    poll_data = response.json()
    assert poll_data["id"] == poll_id
    assert poll_data["title"] == "Test Poll for GET"
    assert len(poll_data["choices"]) == 2
    assert "text" in poll_data["choices"][0]
    assert "votes" in poll_data["choices"][0]


def test_close_poll(client: TestClient, mock_user):
    # 1. Создаем опрос
    create_response = client.post(
        "/polls/polls?token=fake_token",
        json={
            "title": "Test Poll to Close",
            "choices": ["Yes", "No"],
            "token": "fake_token"
        }
    )
    assert create_response.status_code == 200
    poll_id = create_response.json()["id"]

    # 2. Закрываем опрос с новой датой
    close_data = {
        "new_close_date": "2025-05-10T12:00:00Z"
    }

    with patch("app.shared.security.get_current_user", return_value=mock_user):
        close_response = client.post(
            f"/polls/{poll_id}/close?token=fake_token",
            json=close_data
        )
