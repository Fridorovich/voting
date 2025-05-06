from fastapi import APIRouter, Depends, HTTPException
from app.database.session import get_db
from app.modules.voting.services import (
    get_active_polls,
    vote_in_poll,
    get_poll_details,
    close_poll
)
from app.modules.voting.services import create_poll
from app.modules.voting.schemas import (
    PollCreate,
    TokenParam,
    VoteCreate,
    ClosePollRequest
)
from app.shared.security import get_current_user

router = APIRouter(prefix="/polls", tags=["Polls"])


@router.get("/", response_model=list[dict])
async def get_all_active_polls(db=Depends(get_db)):
    """Получение списка всех опросов с результатами"""
    return await get_active_polls(db)


@router.post("/polls")
async def user_create_poll(
        poll_data: PollCreate,
        token_param: TokenParam = Depends(),
        db=Depends(get_db),
):
    """Пользователь создает новый опрос"""
    return await create_poll(db, poll_data)


@router.post("/{poll_id}/vote")
async def user_vote_in_poll(
        poll_id: int,
        vote_data: VoteCreate,
        db=Depends(get_db),
        user=Depends(get_current_user)
):
    """Авторизованный пользователь голосует в опросе"""
    await vote_in_poll(db, poll_id, vote_data.choice_ids, user["email"])
    return {"message": "Vote successful"}


@router.get("/{poll_id}", response_model=dict)
async def get_poll_choices(poll_id: int, db=Depends(get_db)):
    """Получение деталей опроса и его вариантов ответов"""
    poll_details = await get_poll_details(db, poll_id)
    if not poll_details:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll_details


@router.post("/{poll_id}/close")
async def user_close_poll(
        poll_id: int,
        close_data: ClosePollRequest,
        token_param: TokenParam = Depends(),
        db=Depends(get_db),
        user=Depends(get_current_user)
):
    """Создатель опроса может закрыть его или установить новую дату закрытия"""
    await close_poll(db, poll_id, user["email"], close_data.new_close_date)
    return {"message": "Poll closed successfully"}
