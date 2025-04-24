from fastapi import APIRouter, Depends, HTTPException
from app.database.session import get_db
from app.modules.admin.schemas import UserCreate, PollCreate, PollUpdate
from app.modules.admin.services import create_user, create_poll, update_poll, check_and_close_polls, delete_poll, \
    delete_user, get_all_choices

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/users")
async def admin_create_user(user_data: UserCreate, db=Depends(get_db)):
    """Администратор создает нового пользователя"""
    return await create_user(db, user_data)

@router.post("/polls")
async def admin_create_poll(poll_data: PollCreate, db=Depends(get_db)):
    """Администратор создает новый опрос"""
    return await create_poll(db, poll_data)

@router.put("/polls/{poll_id}")
async def admin_update_poll(poll_id: int, poll_update_data: PollUpdate, db=Depends(get_db)):
    """Администратор обновляет существующий опрос"""
    try:
        updated_poll = await update_poll(db, poll_id, poll_update_data)
        return updated_poll
    except ValueError:
        raise HTTPException(status_code=404, detail="Poll not found")

@router.post("/polls/check-and-close")
async def admin_check_and_close_polls(db=Depends(get_db)):
    """Администратор может вызвать эту функцию для закрытия просроченных опросов"""
    return await check_and_close_polls(db)

@router.delete("/polls/{poll_id}", response_model=dict)
async def admin_delete_poll(poll_id: int, db=Depends(get_db)):
    """Администратор удаляет опрос по ID"""
    try:
        return await delete_poll(db, poll_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Poll not found")

@router.delete("/users/{user_id}", response_model=dict)
async def admin_delete_user(user_id: int, db=Depends(get_db)):
    """Администратор удаляет пользователя по ID"""
    try:
        return await delete_user(db, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/choices", response_model=list[dict])
async def get_all_choices_route(db=Depends(get_db)):
    """Получение списка всех вариантов ответов"""
    return await get_all_choices(db)