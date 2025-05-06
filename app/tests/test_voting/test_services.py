import pytest
from sqlalchemy.orm import Session
from app.database.models import User
from fastapi.exceptions import HTTPException
from app.modules.voting.services import (
    create_poll,
    get_poll_details,
    vote_in_poll,
    close_poll
)
from app.modules.voting.schemas import PollCreate, VoteCreate


@pytest.fixture
def create_user(db: Session):
    def _create_user(email: str = "user@example.com"):
        user = User(email=email, hashed_password="fake_hashed_password")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _create_user


@pytest.mark.asyncio
async def test_create_poll(db: Session):
    poll_data = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
        is_multiple_choice=False
    )
    result = await create_poll(db, poll_data, "user@example.com")
    assert "id" in result


@pytest.mark.asyncio
async def test_get_poll_details(db: Session):
    poll_data = PollCreate(
        title="Test Poll",
        choices=["Yes", "No"],
        is_multiple_choice=False
    )
    poll_result = await create_poll(db, poll_data, "user@example.com")
    poll_id = poll_result["id"]

    details = await get_poll_details(db, poll_id)
    assert details["title"] == "Test Poll"
    assert len(details["choices"]) == 2


@pytest.mark.asyncio
async def test_get_poll_details_not_found(db: Session):
    details = await get_poll_details(db, poll_id=999)
    assert details is None


@pytest.mark.asyncio
async def test_vote_in_poll(db: Session):
    user = User(email="user@example.com", hashed_password="fake_hashed_password")
    db.add(user)
    db.commit()

    poll_data = PollCreate(
        title="Vote Test",
        choices=["Option A", "Option B"],
        is_multiple_choice=False
    )
    poll_result = await create_poll(db, poll_data, "user@example.com")
    poll_id = poll_result["id"]

    vote_data = VoteCreate(choice_ids=[1])
    await vote_in_poll(db, poll_id, vote_data.choice_ids, user_email="user@example.com")

    details = await get_poll_details(db, poll_id)
    voted_choice = next(choice for choice in details["choices"] if choice["id"] == 1)
    assert voted_choice["id"] == 1


@pytest.mark.asyncio
async def test_vote_in_poll_invalid_choice(db: Session, create_user):
    create_user(email="user@example.com")

    poll_data = PollCreate(
        title="Vote Test Invalid Choice",
        choices=["A", "B"],
        is_multiple_choice=False
    )
    poll_result = await create_poll(db, poll_data, "user@example.com")
    poll_id = poll_result["id"]

    with pytest.raises(HTTPException) as exc_info:
        await vote_in_poll(db, poll_id, [999], user_email="user@example.com")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid choice IDs"


@pytest.mark.asyncio
async def test_vote_in_closed_poll(db: Session, create_user):
    create_user(email="user@example.com")

    poll_data = PollCreate(
        title="Closed Poll",
        choices=["Yes", "No"],
        is_multiple_choice=False
    )
    poll_result = await create_poll(db, poll_data, "user@example.com")
    poll_id = poll_result["id"]

    await close_poll(db, poll_id, user_email="user@example.com")

    with pytest.raises(HTTPException) as exc_info:
        await vote_in_poll(db, poll_id, [1], user_email="user@example.com")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Poll is closed"
