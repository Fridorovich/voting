from pydantic import BaseModel, field_validator
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

    @field_validator('close_date', mode='before')
    def parse_close_date(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as e:
                raise ValueError("Invalid datetime format") from e
        return value


class TokenParam(BaseModel):
    """Схема для параметра токена"""
    token: str


class ClosePollRequest(BaseModel):
    """Схема для закрытия опроса"""
    new_close_date: str = None
