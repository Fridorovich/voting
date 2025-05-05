from sqlalchemy.orm import Session
from app.database.models import User, Poll, Choice
from app.modules.admin.schemas import UserCreate, PollCreate, PollUpdate
from datetime import datetime, timezone
import logging
from app.shared.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def create_user(db: Session, user_data: UserCreate):
    logger.info(f"Creating admin user: email={user_data.email}")
    hashed_password = "hashed_" + user_data.password
    new_user = User(email=user_data.email, hashed_password=hashed_password, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Admin user created: id={new_user.id}")
    return new_user

async def create_poll(db: Session, poll_data: PollCreate):
    logger.info(f"Creating admin poll: title={poll_data.title}")
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
        logger.error("Admin poll creation failed: missing ID")
        raise ValueError("Failed to create poll: poll ID is missing")

    for choice_text in poll_data.choices:
        new_choice = Choice(text=choice_text, poll_id=new_poll.id)
        db.add(new_choice)

    db.commit()
    logger.info(f"Admin poll created successfully: id={new_poll.id}")
    return {"id": new_poll.id, "title": new_poll.title, "choices": poll_data.choices}

async def update_poll(db: Session, poll_id: int, poll_update_data: PollUpdate):
    logger.info(f"Updating poll: poll_id={poll_id}")
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        logger.error(f"Poll not found for update: poll_id={poll_id}")
        raise ValueError("Poll not found")

    if poll_update_data.title:
        poll.title = poll_update_data.title
    if poll_update_data.description:
        poll.description = poll_update_data.description
    if poll_update_data.is_closed is not None:
        poll.is_closed = poll_update_data.is_closed
    if poll_update_data.close_date:
        poll.close_date = datetime.strptime(poll_update_data.close_date, "%Y-%m-%d %H:%M:%S")

    db.commit()
    db.refresh(poll)
    logger.info(f"Poll updated successfully: poll_id={poll_id}")
    return poll

async def check_and_close_polls(db: Session):
    """Проверяет все опросы и закрывает те, чья дата закрытия уже наступила"""
    current_time = datetime.now(UTC)
    polls_to_close = db.query(Poll).filter(
        Poll.close_date.isnot(None),
        Poll.close_date <= current_time,
        Poll.is_closed == False
    ).all()

    for poll in polls_to_close:
        poll.is_closed = True
        db.commit()
        db.refresh(poll)
    logger.info(f"{len(polls_to_close)} polls have been closed successfully.")
    return {"message": f"{len(polls_to_close)} polls have been closed."}


async def delete_poll(db: Session, poll_id: int):
    """Удаление опроса по ID"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        logger.error(f"Poll not found for delete: poll_id={poll_id}")
        raise ValueError("Poll not found")

    db.delete(poll)
    db.commit()
    logger.info(f"Poll deleted successfully: poll_id={poll_id}")
    return {"message": "Poll deleted successfully"}


async def delete_user(db: Session, user_id: int):
    """Удаление пользователя по ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User not found for delete: user_id={user_id}")
        raise ValueError("User not found")

    db.delete(user)
    db.commit()
    logger.info(f"User deleted successfully: user_id={user_id}")
    return {"message": "User deleted successfully"}


async def get_all_choices(db: Session):
    """Получение списка всех вариантов ответов (choices)"""
    choices = db.query(Choice).all()
    return [{"id": choice.id, "text": choice.text, "poll_id": choice.poll_id} for choice in choices]
