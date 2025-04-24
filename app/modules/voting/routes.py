from fastapi import APIRouter, Depends
from app.database.session import get_db
from app.modules.voting.services import get_active_polls

router = APIRouter(prefix="/polls", tags=["Polls"])

@router.get("/", response_model=list[dict])
async def get_all_active_polls(db=Depends(get_db)):
    """Получение списка всех опросов с результатами"""
    return await get_active_polls(db)