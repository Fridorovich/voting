from pydantic import BaseModel, field_validator
from datetime import datetime


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    email: str
    password: str


class PollCreate(BaseModel):
    """Схема для создания опроса"""
    title: str
    description: str = None
    choices: list[str]
    is_multiple_choice: bool = False
    close_date: datetime = None

    @field_validator('close_date', mode='before')
    def parse_close_date(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as e:
                raise ValueError("Invalid datetime format") from e
        return value


class PollUpdate(BaseModel):
    """Схема для обновления опроса"""
    title: str = None
    description: str = None
    is_closed: bool = None
    close_date: str = None


class TokenParam(BaseModel):
    """Схема для параметра токена"""
    token: str
