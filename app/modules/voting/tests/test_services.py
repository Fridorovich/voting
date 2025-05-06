# app/modules/voting/tests/test_services.py

import pytest
from sqlalchemy.orm import Session

from app.modules.voting.services import create_poll, get_poll_details
from app.modules.voting.schemas import PollCreate


def test_create_and_get_poll(db: Session):
    poll_data = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
        is_multiple_choice=False
    )
    result = create_poll(db, poll_data)
    poll_id = result["id"]

    details = get_poll_details(db, poll_id)
    assert details["title"] == "Test Poll"
    assert len(details["choices"]) == 2
