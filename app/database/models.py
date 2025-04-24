from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    polls = relationship("Poll", back_populates="creator")

class Poll(Base):
    __tablename__ = "polls"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="polls")
    creation_date = Column(DateTime, nullable=True)
    is_closed = Column(Boolean, default=False)
    close_date = Column(DateTime, nullable=True)
    is_multiple_choice = Column(Boolean, default=False)
    choices = relationship("Choice", back_populates="poll")

class Choice(Base):
    __tablename__ = "choices"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True, nullable=False)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    poll = relationship("Poll", back_populates="choices")
    votes = relationship("Vote", back_populates="choice")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    choice_id = Column(Integer, ForeignKey("choices.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    choice = relationship("Choice", back_populates="votes")