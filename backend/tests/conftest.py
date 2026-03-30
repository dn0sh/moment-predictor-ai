# AI-generated: окружение pytest — in-memory SQLite и ослабленный rate limit до импорта приложения
import os

# Обязательно до импорта config / database / main
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "pytest-secret-key-at-least-32-chars-long!!"
os.environ["ADMIN_API_KEY"] = "pytest-admin-key"

import pytest
from fastapi.testclient import TestClient

import config

config.get_settings.cache_clear()

from database import Base, engine
from main import app


@pytest.fixture
def client():
    """Чистая схема перед каждым тестом (общий StaticPool :memory:)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
