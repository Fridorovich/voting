from pydantic import BaseModel, validator
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str

class PollCreate(BaseModel):
    title: str
    description: str = None
    choices: list[str]
    is_multiple_choice: bool = False
    close_date: datetime = None

    @validator("close_date", pre=True)
    def parse_close_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))  # Поддержка ISO 8601
            except ValueError:
                raise ValueError("Invalid datetime format")
        return value
class PollUpdate(BaseModel):
    title: str = None
    description: str = None
    is_closed: bool = None
    close_date: str = None

class TokenParam(BaseModel):
    """Схема для параметра токена"""
    token: str