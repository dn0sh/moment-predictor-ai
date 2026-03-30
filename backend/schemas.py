# AI-generated: Pydantic-схемы запросов и ответов API
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, computed_field

from prediction_scoring import prediction_points_for_event


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=4, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    total_points: int
    total_predictions: int
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class PredictionCreate(BaseModel):
    video_id: str = Field(..., max_length=128)
    video_timestamp: float = Field(..., description="Seconds on video timeline")
    event_type: str = Field(..., max_length=64)


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    video_id: str
    video_timestamp: float
    event_type: str
    created_at: datetime
    accuracy_score: float | None

    @computed_field
    @property
    def points_earned(self) -> int:
        return prediction_points_for_event(self.event_type)


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_points: int
    total_predictions: int


class EventCreate(BaseModel):
    video_id: str = Field(..., max_length=128)
    timestamp: float
    event_type: str = Field(..., max_length=64)
    confirmed_by_admin: bool = True


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    video_id: str
    timestamp: float
    event_type: str
    confirmed_by_admin: bool


class StatsResponse(BaseModel):
    total_users: int
    total_predictions: int
    total_events: int
    average_accuracy: float | None
