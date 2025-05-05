from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.auth.schemas import UserCreate, UserLogin, Token
from app.modules.auth.services import create_user, authenticate_user, create_access_token, create_refresh_token, decode_access_token
from app.database.session import get_db
from app.database.models import User
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db=Depends(get_db)):
    """Регистрация нового пользователя"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    await create_user(db, user_data.email, user_data.password)
    return {"message": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db=Depends(get_db)):
    """Логин пользователя"""
    user = await authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_data = {
        "sub": user.email,
        "role": user.role
    }
    refresh_token_data = {
        "sub": user.email,
        "role": user.role
    }

    access_token = create_access_token(
        data=access_token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data=refresh_token_data,
        expires_delta=timedelta(days=7)
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout", response_model=dict)
async def logout():
    """Выход из аккаунта (необходимо очистить токен на клиенте)"""
    return {"message": "Logout successful"}


@router.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Обновление access token с использованием refresh token"""
    payload = decode_access_token(refresh_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": payload["sub"], "role": payload["role"]}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh_token = create_refresh_token(data={"sub": payload["sub"], "role": payload["role"]}, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
