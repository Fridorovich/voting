from pydantic import BaseModel


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    email: str
    password: str


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: str
    password: str


class Token(BaseModel):
    """Схема для ответа с токеном"""
    access_token: str
    refresh_token: str
    token_type: str
