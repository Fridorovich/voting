import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from app.modules.voting.services import get_active_polls
from app.database.models import Poll, Choice, Vote
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_get_active_polls_with_closed_poll():
    mock_poll = Poll(
        id=1,
        title="Test Poll",
        description="Test Description",
        close_date=datetime.now() - timedelta(days=1),
        is_closed=True,
        choices=[
            Choice(id=1, text="Option 1"),
            Choice(id=2, text="Option 2")
        ]
    )
    
    mock_votes = [
        Vote(choice_id=1),
        Vote(choice_id=1),
        Vote(choice_id=2)
    ]
    
    mock_db = MagicMock(spec=Session)
    mock_db.query.return_value.all.return_value = [mock_poll]
    
    vote_query = MagicMock()
    vote_query.filter.return_value.all.return_value = mock_votes
    mock_db.query.return_value = vote_query
    
    result = await get_active_polls(mock_db)
    
    assert len(result) == 1
    assert result[0]["title"] == "Test Poll"
    assert result[0]["results"] == {"Option 1": 2, "Option 2": 1}
    assert result[0]["is_closed"] is True

@pytest.mark.asyncio
async def test_get_active_polls_with_open_poll():
    mock_poll = Poll(
        id=1,
        title="Test Poll",
        description="Test Description",
        close_date=datetime.now() + timedelta(days=1),
        is_closed=False,
        choices=[
            Choice(id=1, text="Option 1"),
            Choice(id=2, text="Option 2")
        ]
    )
    mock_db = MagicMock(spec=Session)
    mock_db.query.return_value.all.return_value = [mock_poll]
    
    result = await get_active_polls(mock_db)
    
    assert len(result) == 1
    assert result[0]["title"] == "Test Poll"
    assert result[0]["results"] == {}
    assert result[0]["is_closed"] is False