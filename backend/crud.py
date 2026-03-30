# AI-generated: операции с БД — пользователи, прогнозы, события, лидерборд, статистика
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_password_hash, verify_password
from prediction_scoring import prediction_points_for_event

# Окно попадания (секунды), совпадает с формулой accuracy_score
ACCURACY_WINDOW_SEC = 30.0


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    user = models.User(
        username=data.username,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_prediction(db: Session, user: models.User, data: schemas.PredictionCreate) -> models.Prediction:
    # Очки за прогноз — по типу события (prediction_scoring); точность — после POST /api/event
    pred = models.Prediction(
        user_id=user.id,
        video_id=data.video_id,
        video_timestamp=data.video_timestamp,
        event_type=data.event_type,
    )
    pts = prediction_points_for_event(data.event_type)
    user.total_predictions += 1
    user.total_points += pts
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def get_leaderboard_top(db: Session, limit: int = 10) -> list[models.User]:
    return (
        db.query(models.User)
        .order_by(models.User.total_points.desc(), models.User.id.asc())
        .limit(limit)
        .all()
    )


def get_predictions_for_user(db: Session, user_id: int) -> list[models.Prediction]:
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.user_id == user_id)
        .order_by(models.Prediction.created_at.desc())
        .all()
    )


def create_event_and_score_predictions(db: Session, data: schemas.EventCreate) -> models.Event:
    # AI-generated: accuracy_score = 1 - min(1, abs(t_pred - t_event) / 30)
    ev = models.Event(
        video_id=data.video_id,
        timestamp=data.timestamp,
        event_type=data.event_type,
        confirmed_by_admin=data.confirmed_by_admin,
    )
    db.add(ev)
    db.flush()

    preds = (
        db.query(models.Prediction)
        .filter(
            models.Prediction.video_id == data.video_id,
            models.Prediction.event_type == data.event_type,
        )
        .all()
    )
    for p in preds:
        p.accuracy_score = 1.0 - min(1.0, abs(p.video_timestamp - data.timestamp) / ACCURACY_WINDOW_SEC)

    db.commit()
    db.refresh(ev)
    return ev


def get_stats(db: Session) -> schemas.StatsResponse:
    total_users = db.query(func.count(models.User.id)).scalar() or 0
    total_predictions = db.query(func.count(models.Prediction.id)).scalar() or 0
    total_events = db.query(func.count(models.Event.id)).scalar() or 0
    avg = db.query(func.avg(models.Prediction.accuracy_score)).filter(
        models.Prediction.accuracy_score.isnot(None)
    ).scalar()
    return schemas.StatsResponse(
        total_users=total_users,
        total_predictions=total_predictions,
        total_events=total_events,
        average_accuracy=float(avg) if avg is not None else None,
    )
