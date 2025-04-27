from sqlalchemy.orm import Session
from app.database.models import User, Poll, Choice
from app.modules.admin.schemas import UserCreate, PollCreate, PollUpdate
from datetime import datetime, timezone, UTC


async def create_user(db: Session, user_data: UserCreate):
    """Создание нового пользователя"""
    hashed_password = "hashed_" + user_data.password
    new_user = User(email=user_data.email, hashed_password=hashed_password, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


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


async def update_poll(db: Session, poll_id: int, poll_update_data: PollUpdate):
    """Обновление существующего опроса"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
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

    return {"message": f"{len(polls_to_close)} polls have been closed."}


async def delete_poll(db: Session, poll_id: int):
    """Удаление опроса по ID"""
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise ValueError("Poll not found")

    db.delete(poll)
    db.commit()
    return {"message": "Poll deleted successfully"}


async def delete_user(db: Session, user_id: int):
    """Удаление пользователя по ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


async def get_all_choices(db: Session):
    """Получение списка всех вариантов ответов (choices)"""
    choices = db.query(Choice).all()
    return [{"id": choice.id, "text": choice.text, "poll_id": choice.poll_id} for choice in choices]
