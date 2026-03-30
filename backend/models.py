# AI-generated: ORM-модели User, Prediction, Event
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    total_points = Column(Integer, default=0, nullable=False)
    total_predictions = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    predictions = relationship("Prediction", back_populates="user")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(String(128), nullable=False, index=True)
    video_timestamp = Column(Float, nullable=False)
    event_type = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accuracy_score = Column(Float, nullable=True)

    user = relationship("User", back_populates="predictions")

    __table_args__ = (Index("ix_predictions_video_event", "video_id", "event_type"),)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(128), nullable=False, index=True)
    timestamp = Column(Float, nullable=False)
    event_type = Column(String(64), nullable=False)
    confirmed_by_admin = Column(Boolean, default=True, nullable=False)
