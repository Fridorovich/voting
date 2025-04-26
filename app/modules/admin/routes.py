from fastapi import APIRouter, Depends, HTTPException, status
from app.database.session import get_db
from app.modules.admin.schemas import UserCreate, PollCreate, PollUpdate, TokenParam
from app.modules.admin.services import (
    create_user,
    create_poll,
    update_poll,
    check_and_close_polls,
    delete_poll,
    delete_user,
    get_all_choices,
)
from app.shared.security import get_current_admin  # Защита админских эндпоинтов

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/users")
async def admin_create_user(
    user_data: UserCreate,
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Администратор создает нового пользователя"""
    return await create_user(db, user_data.email, user_data.password, role="user")

@router.post("/polls")
async def admin_create_poll(
    poll_data: PollCreate,
    token_param: TokenParam = Depends(),  # Токен как параметр запроса
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Администратор создает новый опрос"""
    return await create_poll(db, poll_data)

@router.put("/polls/{poll_id}")
async def admin_update_poll(
    poll_id: int,
    poll_update_data: PollUpdate,
    token_param: TokenParam = Depends(),  # Токен как параметр запроса
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Администратор обновляет существующий опрос"""
    try:
        updated_poll = await update_poll(db, poll_id, poll_update_data)
        return updated_poll
    except ValueError:
        raise HTTPException(status_code=404, detail="Poll not found")

@router.post("/polls/check-and-close")
async def admin_check_and_close_polls(
    token_param: TokenParam = Depends(),  # Токен как параметр запроса
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Администратор может вызвать эту функцию для закрытия просроченных опросов"""
    return await check_and_close_polls(db)

@router.delete("/polls/{poll_id}")
async def admin_delete_poll(
    poll_id: int,
    token_param: TokenParam = Depends(),  # Токен как параметр запроса
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Администратор удаляет опрос по ID"""
    try:
        return await delete_poll(db, poll_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Poll not found")

@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    token_param: TokenParam = Depends(),  # Токен как параметр запроса
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Администратор удаляет пользователя по ID"""
    try:
        return await delete_user(db, user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/choices")
async def get_all_choices_route(
    token_param: TokenParam = Depends(),  # Токен как параметр запроса
    db=Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Получение списка всех вариантов ответов"""
    return await get_all_choices(db)