from sqlalchemy.orm import Session
from app.database.models import Poll, Choice, Vote
from collections import Counter


async def get_active_polls(db: Session):
    """Получение списка всех активных опросов с результатами"""
    active_polls = db.query(Poll).all()

    result = []
    for poll in active_polls:
        poll_data = {
            "id": poll.id,
            "title": poll.title,
            "description": poll.description,
            "close_date": poll.close_date.isoformat() if poll.close_date else None,
            "is_closed": poll.is_closed,
            "results": {}
        }

        if poll.is_closed:
            votes = db.query(Vote.choice_id).filter(Vote.choice_id.in_([c.id for c in poll.choices])).all()
            vote_counts = Counter(vote.choice_id for vote in votes)
            poll_data["results"] = {choice.text: vote_counts.get(choice.id, 0) for choice in poll.choices}

        result.append(poll_data)

    return result