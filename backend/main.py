# AI-generated: FastAPI-приложение — CORS, rate limit, JWT, админ-ключ, роуты API
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import crud
import models  # noqa: F401 — регистрация таблиц для create_all
import schemas
from auth import create_access_token, get_current_user
from config import get_settings
from database import Base, engine, get_db

limiter = Limiter(key_func=get_remote_address)

# В pytest выставляется TESTING=1 до импорта main — лимит завышен, чтобы не ломать TestClient
_API_RATE = "1000/minute" if os.getenv("TESTING") == "1" else "10/minute"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Moment Predictor API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# AI-generated: для демо разрешены все origins; в production задайте конкретные домены вместо "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_admin_key(x_admin_key: str | None = Header(None, alias="X-Admin-Key")) -> bool:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing X-Admin-Key")
    return True


@app.get("/")
def root():
    # Подсказка при открытии http://127.0.0.1:8000/ вместо «голого» 404
    return {
        "service": "Moment Predictor API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=schemas.UserRead)
@limiter.limit(_API_RATE)
def register(request: Request, data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Имя пользователя уже занято.")


@app.post("/api/auth/login", response_model=schemas.Token)
@limiter.limit(_API_RATE)
def login(request: Request, data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(user.id)
    return schemas.Token(access_token=token)


@app.post("/api/prediction", response_model=schemas.PredictionRead)
@limiter.limit(_API_RATE)
def create_prediction(
    request: Request,
    data: schemas.PredictionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_prediction(db, current_user, data)


@app.get("/api/leaderboard", response_model=list[schemas.LeaderboardEntry])
@limiter.limit(_API_RATE)
def leaderboard(request: Request, db: Session = Depends(get_db)):
    rows = crud.get_leaderboard_top(db, limit=10)
    return [
        schemas.LeaderboardEntry(
            rank=i + 1,
            username=u.username,
            total_points=u.total_points,
            total_predictions=u.total_predictions,
        )
        for i, u in enumerate(rows)
    ]


@app.get("/api/predictions/{user_id}", response_model=list[schemas.PredictionRead])
@limiter.limit(_API_RATE)
def user_predictions(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only access own predictions")
    return crud.get_predictions_for_user(db, user_id)


@app.post("/api/event", response_model=schemas.EventRead)
@limiter.limit(_API_RATE)
def confirm_event(
    request: Request,
    data: schemas.EventCreate,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_admin_key),
):
    return crud.create_event_and_score_predictions(db, data)


@app.get("/api/stats", response_model=schemas.StatsResponse)
@limiter.limit(_API_RATE)
def stats(request: Request, db: Session = Depends(get_db)):
    return crud.get_stats(db)
