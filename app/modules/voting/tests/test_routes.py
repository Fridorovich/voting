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
    # Создаем опрос
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

    # Голосуем
    with patch("app.shared.security.get_current_user", return_value=mock_user):
        vote_response = client.post(
            f"/polls/{poll_id}/vote?token=fake_token",
            json={"choice_ids": [1]}
        )
    assert vote_response.status_code == 200


def test_get_poll_details(client: TestClient):
    create_response = client.post(
        "/polls/polls?token=fake_token",
        json={
            "title": "Details Test",
            "choices": ["Yes", "No"],
            "token": "fake_token"
        }
    )
    assert create_response.status_code == 200
    poll_id = create_response.json()["id"]

    response = client.get(f"/polls/{poll_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Details Test"


def test_close_poll(client: TestClient, mock_user):
    create_response = client.post(
        "/polls/polls?token=fake_token",
        json={
            "title": "Close Test",
            "choices": ["Yes", "No"],
            "token": "fake_token"
        }
    )
    assert create_response.status_code == 200
    poll_id = create_response.json()["id"]

    close_payload = {"new_close_date": "2025-05-10T12:00:00Z"}
    with patch("app.shared.security.get_current_user", return_value=mock_user):
        response = client.post(f"/polls/{poll_id}/close?token=fake_token", json=close_payload)
    assert response.status_code == 200
