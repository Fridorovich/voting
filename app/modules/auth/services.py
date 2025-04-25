from sqlalchemy.orm import Session
from app.database.models import User
from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta, datetime
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: Session, email: str, password: str, role: str = "user"):
    """Регистрация нового пользователя"""
    hashed_password = pwd_context.hash(password)
    new_user = User(email=email, hashed_password=hashed_password, is_active=True, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def authenticate_user(db: Session, email: str, password: str):
    """Аутентификация пользователя"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT-токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Декодирование JWT-токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """Создание refresh токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
