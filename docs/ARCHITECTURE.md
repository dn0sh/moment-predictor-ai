# Архитектура Moment Predictor (backend)

## Слои

1. **HTTP (FastAPI)** — маршруты в `backend/main.py`, валидация тел через Pydantic (`schemas.py`).
2. **Авторизация** — JWT в заголовке `Authorization: Bearer …` (`auth.py`); пароли — **bcrypt** (без passlib, чтобы не тянуть устаревшие связки с bcrypt 5). Админские действия — заголовок `X-Admin-Key` (сверка с `ADMIN_API_KEY` в `.env`, без ролей в БД).
3. **Бизнес-логика и доступ к данным** — `crud.py`.
4. **Персистентность** — SQLAlchemy ORM (`models.py`), SQLite файл (`database.py`).

## Модели данных

- **User** — игрок, агрегаты `total_points`, `total_predictions`.
- **Prediction** — прогноз по `video_id`, секунде `video_timestamp`, типу `event_type`; после подтверждения события заполняется `accuracy_score`.
- **Event** — факт события на видео (подтверждение админом).

## Точность прогноза

После `POST /api/event` для всех прогнозов с тем же `video_id` и `event_type`:

`accuracy_score = 1 - min(1, abs(t_pred - t_event) / 30)`  

(окно «попадания» — 30 секунд.)

## Ограничение частоты

**SlowAPI**: до **10 запросов в минуту** с одного IP на каждый защищённый лимитом маршрут. `/health` без лимита.

## CORS

Для демо: `allow_origins=["*"]`. В production нужно указать явный список доменов фронтенда.

## Docker

Проект **`moment-predictor`**: сервис **`moment-api`** (FastAPI, порт хоста **8119**), **`moment-web`** (nginx, **8118**) — статика `frontend/` и прокси `/api/`, `/health`, `/docs`. SQLite в именованном томе **`moment_predictor_sqlite`** → `/app/data` в API-контейнере. См. [docker/docker-compose.yml](../docker/docker-compose.yml).

## Тесты

- `backend/tests/` — pytest + `TestClient`, БД `sqlite:///:memory:` (StaticPool), переменная **`TESTING=1`** задаётся в `conftest.py` до импорта `main` и ослабляет rate limit для стабильного прогона.
- `test_quick.py` в корне — ручная проверка против живого `uvicorn` (библиотека `requests`).
