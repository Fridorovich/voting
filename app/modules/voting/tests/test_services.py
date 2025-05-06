# app/modules/voting/tests/test_services.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.modules.voting.services import create_poll, get_poll_details, vote_in_poll
from app.modules.voting.schemas import PollCreate


@pytest.mark.asyncio
async def test_create_and_get_poll(db_session: AsyncSession):
    poll_data = PollCreate(
        title="Test Poll",
        description="A test poll",
        choices=["Yes", "No"],
        is_multiple_choice=False,
        close_date=datetime.utcnow() + timedelta(days=1),
    )
    poll_id = await create_poll(db_session, poll_data)
    assert poll_id > 0

    details = await get_poll_details(db_session, poll_id)
    assert details["title"] == "Test Poll"
    assert len(details["choices"]) == 2


@pytest.mark.asyncio
async def test_vote_in_poll(db_session: AsyncSession):
    poll_data = PollCreate(
        title="Vote Test",
        choices=["Option A", "Option B"],
        is_multiple_choice=False
    )
    poll_id = await create_poll(db_session, poll_data)

    user_email = "user@example.com"
    await vote_in_poll(db_session, poll_id, [1], user_email)

    details = await get_poll_details(db_session, poll_id)
    voted_choice = next(choice for choice in details["choices"] if choice["id"] == 1)
    assert voted_choice["votes"] == 1
