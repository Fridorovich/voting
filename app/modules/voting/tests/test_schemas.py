# app/modules/voting/tests/test_schemas.py

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.modules.voting.schemas import PollCreate


def test_poll_create_valid():
    poll = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
    )
    assert poll.title == "Test Poll"
    assert poll.choices == ["Yes", "No"]


def test_poll_create_with_description():
    poll = PollCreate(
        title="Test Poll",
        description="This is a test poll",
        choices=["Yes", "No"],
    )
    assert poll.description == "This is a test poll"


def test_poll_create_multiple_choice():
    poll = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
        is_multiple_choice=True,
    )
    assert poll.is_multiple_choice is True


def test_poll_create_with_close_date_isoformat():
    iso_date_str = "2025-12-31T23:59:59Z"
    poll = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
        close_date=iso_date_str,
    )
    expected_dt = datetime.fromisoformat("2025-12-31T23:59:59+00:00")
    assert poll.close_date == expected_dt


def test_poll_create_with_invalid_close_date():
    with pytest.raises(ValidationError):
        PollCreate(
            title="Test Poll",
            choices=["Yes", "No"],
            close_date="invalid-date-format",
        )


def test_poll_create_with_datetime_object():
    now = datetime.utcnow()
    poll = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
        close_date=now,
    )
    assert poll.close_date == now
