from datetime import timezone, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.models import Poll, Choice, Vote, User
from collections import Counter

from app.modules.voting.schemas import PollCreate


async def get_active_polls(db: Session):
    """Получение списка всех активных опросов с результатами"""
    all_polls = db.query(Poll).all()

    result = []
    for poll in all_polls:
        poll_data = {
            "id": poll.id,
            "title": poll.title,
            "description": poll.description,
            "close_date": poll.close_date.isoformat() if poll.close_date else None,
            "is_closed": poll.is_closed,
            "results": {}
        }

        if poll.is_closed:
            votes = db.query(Vote.choice_id).filter(
                Vote.choice_id.in_([c.id for c in poll.choices])
            ).all()

            vote_counts = Counter(vote.choice_id for vote in votes)

            poll_data["results"] = {
                choice.text: vote_counts.get(choice.id, 0)
                for choice in poll.choices
            }

        else:
            poll_data["results"] = {
                choice.text: 0
                for choice in poll.choices
            }

        result.append(poll_data)

    return result


async def create_poll(db: Session, poll_data: PollCreate):
    """Создание нового опроса с датой закрытия"""
    new_poll = Poll(
        title=poll_data.title,
        description=poll_data.description,
        creator_id=1,
        is_multiple_choice=poll_data.is_multiple_choice,
        close_date=poll_data.close_date,
        is_closed=False,
        creation_date=datetime.now(timezone.utc)
    )

    db.add(new_poll)
    db.commit()
    db.refresh(new_poll)

    if not new_poll.id:
        raise ValueError("Failed to create poll: poll ID is missing")

    for choice_text in poll_data.choices:
        new_choice = Choice(text=choice_text, poll_id=new_poll.id)
        db.add(new_choice)
    db.commit()

    return {"id": new_poll.id, "title": new_poll.title, "choices": poll_data.choices}


async def vote_in_poll(db: Session, poll_id: int, choice_ids: list[int], user_email: str):
    """Голосование пользователя в опросе"""
    # Находим опрос
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    if poll.is_closed:
        raise HTTPException(status_code=400, detail="Poll is closed")

    close_date = poll.close_date
    if close_date and not close_date.tzinfo:
        close_date = close_date.replace(tzinfo=timezone.utc)

    if close_date and close_date <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Poll has expired")

    choices = db.query(Choice).filter(Choice.id.in_(choice_ids), Choice.poll_id == poll_id).all()
    if len(choices) != len(choice_ids):
        raise HTTPException(status_code=400, detail="Invalid choice IDs")

    if not poll.is_multiple_choice and len(choice_ids) > 1:
        raise HTTPException(status_code=400, detail="Single-choice poll cannot have multiple selections")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_votes = (
        db.query(Vote)
        .filter(
            Vote.user_id == user.id,
            Vote.choice_id.in_([c.id for c in poll.choices])
        )
        .all()
    )

    if existing_votes:
        for vote in existing_votes:
            db.delete(vote)

    new_votes = [
        Vote(user_id=user.id, choice_id=choice_id)
        for choice_id in choice_ids
    ]
    db.add_all(new_votes)
    db.commit()

    return {"message": "Vote processed successfully"}


async def get_poll_details(db: Session, poll_id: int):
    """Получение деталей опроса и его вариантов ответов"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        return None

    choices = db.query(Choice).filter(Choice.poll_id == poll_id).all()
    return {
        "id": poll.id,
        "title": poll.title,
        "description": poll.description,
        "is_multiple_choice": poll.is_multiple_choice,
        "close_date": poll.close_date.isoformat() if poll.close_date else None,
        "is_closed": poll.is_closed,
        "choices": [{"id": choice.id, "text": choice.text} for choice in choices]
    }


async def close_poll(db: Session, poll_id: int, user_email: str, new_close_date: str = None):
    """Закрытие опроса создателем"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    if poll.is_closed:
        raise HTTPException(status_code=400, detail="Poll already closed")

    if poll.creator.email != user_email:
        raise HTTPException(status_code=403, detail="Only the creator of the poll can close it")

    if new_close_date:
        try:
            poll.close_date = datetime.fromisoformat(new_close_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid close date format")

    poll.is_closed = True
    db.commit()
    db.refresh(poll)

    return {"message": "Poll closed successfully"}
