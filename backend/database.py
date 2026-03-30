# AI-generated: движок SQLite, сессии и базовый класс моделей
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from config import get_settings

settings = get_settings()


def _resolve_sqlite_url(url: str) -> str:
    if not url.startswith("sqlite"):
        return url
    path_str = url.replace("sqlite:///", "", 1)
    if path_str == ":memory:":
        return ":memory:"
    db_path = Path(path_str)
    if not db_path.is_absolute():
        db_path = Path(__file__).resolve().parent / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


SQLALCHEMY_DATABASE_URL = _resolve_sqlite_url(settings.database_url)

if SQLALCHEMY_DATABASE_URL == ":memory:":
    # Один общий in-memory SQLite для всех соединений (pytest, :memory:)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
