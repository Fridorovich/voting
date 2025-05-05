from pydantic import BaseModel, validator
from datetime import datetime


class VoteCreate(BaseModel):
    """Схема для голосования"""
    choice_ids: list[int]


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
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Invalid datetime format")
        return value


class TokenParam(BaseModel):
    """Схема для параметра токена"""
    token: str


class ClosePollRequest(BaseModel):
    """Схема для закрытия опроса"""
    new_close_date: str = None
