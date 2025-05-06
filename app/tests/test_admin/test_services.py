import pytest
from unittest.mock import MagicMock
from datetime import timedelta
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.models import User, Poll, Choice
from app.modules.admin.schemas import UserCreate, PollCreate, PollUpdate
from app.modules.admin.services import (
    create_user,
    create_poll,
    update_poll,
    check_and_close_polls,
    delete_poll,
    delete_user,
    get_all_choices,
)

UTC = timezone.utc


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def user_data():
    return UserCreate(email="test@example.com", password="password123")


@pytest.fixture
def poll_data():
    return PollCreate(
        title="Test Poll",
        description="Test Description",
        is_multiple_choice=True,
        close_date=datetime.now(timezone.utc) + timedelta(days=1),
        choices=["Choice 1", "Choice 2"]
    )


@pytest.fixture
def poll_update_data():
    return PollUpdate(
        title="Updated Poll",
        description="Updated Description",
        is_closed=True,
        close_date=(
                datetime.now(timezone.utc) +
                timedelta(days=2)
        ).strftime("%Y-%m-%d %H:%M:%S")
    )


@pytest.mark.asyncio
async def test_create_user_success(mock_db, user_data):
    mock_user = User(
        id=1,
        email=user_data.email,
        hashed_password="hashed_password123",
        is_active=True
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = await create_user(mock_db, user_data)

    assert result.email == user_data.email
    assert "hashed_" in result.hashed_password
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_poll_success(mock_db, poll_data):
    mock_poll = MagicMock(spec=Poll)
    mock_poll.id = 1
    mock_poll.title = poll_data.title
    mock_poll = Poll(
        id=1,
        title=poll_data.title,
        description=poll_data.description,
        creator_id=1,
        is_multiple_choice=poll_data.is_multiple_choice,
        close_date=poll_data.close_date,
        is_closed=False
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    def refresh_mock(poll):
        poll.id = 1

    mock_db.refresh.side_effect = refresh_mock

    result = await create_poll(mock_db, poll_data)
    assert result["id"] == 1
    assert result["title"] == poll_data.title
    assert len(result["choices"]) == 2
    assert mock_db.add.call_count == 3
    assert mock_db.commit.call_count == 2


@pytest.mark.asyncio
async def test_create_poll_failure(mock_db, poll_data):
    mock_poll = Poll(
        title=poll_data.title,
        description=poll_data.description,
        creator_id=1,
        is_multiple_choice=poll_data.is_multiple_choice,
        close_date=poll_data.close_date,
        is_closed=False
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    with pytest.raises(ValueError, match="Failed to create poll: poll ID is missing"):
        await create_poll(mock_db, poll_data)


@pytest.mark.asyncio
async def test_update_poll_success(mock_db, poll_update_data):
    existing_poll = Poll(
        id=1,
        title="Original Title",
        description="Original Description",
        is_closed=False,
        close_date=datetime.now(timezone.utc)
    )
    mock_db.query.return_value.filter.return_value.first.return_value = existing_poll

    result = await update_poll(mock_db, 1, poll_update_data)

    assert result.title == poll_update_data.title
    assert result.description == poll_update_data.description
    assert result.is_closed == poll_update_data.is_closed
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_poll_not_found(mock_db, poll_update_data):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Poll not found"):
        await update_poll(mock_db, 999, poll_update_data)


@pytest.mark.asyncio
async def test_check_and_close_polls(mock_db):
    now = datetime.now(timezone.utc)
    open_poll = Poll(id=1, close_date=now - timedelta(hours=1), is_closed=False)
    # closed_poll = Poll(id=2, close_date=now - timedelta(days=1), is_closed=True)
    # future_poll = Poll(id=3, close_date=now + timedelta(days=1), is_closed=False)

    mock_db.query.return_value.filter.return_value.all.return_value = [open_poll]

    result = await check_and_close_polls(mock_db)

    assert result["message"] == "1 polls have been closed."
    assert open_poll.is_closed is True
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_poll_success(mock_db):
    existing_poll = Poll(id=1, title="Test Poll")
    mock_db.query.return_value.filter.return_value.first.return_value = existing_poll

    result = await delete_poll(mock_db, 1)

    assert result["message"] == "Poll deleted successfully"
    mock_db.delete.assert_called_once_with(existing_poll)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_poll_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Poll not found"):
        await delete_poll(mock_db, 999)


@pytest.mark.asyncio
async def test_delete_user_success(mock_db):
    existing_user = User(id=1, email="test@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = existing_user

    result = await delete_user(mock_db, 1)

    assert result["message"] == "User deleted successfully"
    mock_db.delete.assert_called_once_with(existing_user)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_choices(mock_db):
    choice1 = Choice(id=1, text="Choice 1", poll_id=1)
    choice2 = Choice(id=2, text="Choice 2", poll_id=1)
    mock_db.query.return_value.all.return_value = [choice1, choice2]

    result = await get_all_choices(mock_db)

    assert len(result) == 2
    assert result[0]["text"] == "Choice 1"
    assert result[1]["text"] == "Choice 2"
