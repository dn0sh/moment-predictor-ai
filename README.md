# Moment Predictor

AI-powered sports prediction game.

## AI-First Development

| Component | Tool | Time |
|-----------|------|------|
| Frontend | Google AI Studio (Gemini) | 2 hours |
| Backend | Cursor (Claude) | 1 hour |
| **Total** | | **3 hours** |

## Quick Start

### Frontend (vanilla JS)

Список роликов YouTube по категориям задаётся в **[frontend/videos.config.js](frontend/videos.config.js)** (`window.MP_VIDEO_CONFIG`) — меняйте `id` и `title` там, без правок `index.html`.

Open [frontend/index.html](frontend/index.html) in the browser, or run a static server (лучше **привязать к IPv4**, чтобы совпадал с `API_BASE_URL` на `127.0.0.1`):

```bash
python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

Затем откройте http://127.0.0.1:8080/

### Backend (FastAPI)

Целевая версия **Python 3.12**. Создание окружения в корне репозитория (Windows):

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

From the **repository root** (используйте только `.venv` проекта):

```bash
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

On Linux/macOS (Python 3.12):

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r backend/requirements.txt
cd backend
../.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Copy [.env.example](.env.example) to `.env` in the **project root** and set `SECRET_KEY` and `ADMIN_API_KEY`. For a quick local run, defaults in [backend/config.py](backend/config.py) match `dev-secret-change-in-production` / `dev-admin-key-change-me` if variables are unset — still prefer a real `.env` for anything beyond local demos.

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Docker

Стек изолирован **именем проекта** `moment-predictor` и сетью **`moment_predictor_net`**, чтобы не пересекаться с другими compose-проектами на машине.

Порты на хосте (заданный вами диапазон):

| Порт | Назначение |
|------|------------|
| **8118** | Сайт (nginx): `index.html`, `videos.config.js`, прокси **`/api/*`**, **`/health`**, **`/docs`** |
| **8119** | FastAPI напрямую (удобно для Postman и `/docs`) |
| *8117, 8116* | Не используются этим compose — зарезервированы под расширение (например БД) |

Из **корня репозитория** (нужен `.env`, см. `.env.example`):

```bash
docker compose -f docker/docker-compose.yml up --build -d
```

Откройте **http://127.0.0.1:8118/** — фронт подхватывает `docker/nginx/api-config.js` с пустым базовым URL, запросы идут на тот же хост через nginx. SQLite лежит в томе **`moment_predictor_sqlite`**.

Локальная разработка без Docker по-прежнему использует `http://127.0.0.1:8000`; при необходимости задайте `window.MP_API_BASE_URL` в **[frontend/api-config.js](frontend/api-config.js)** (например `http://127.0.0.1:8119`).

## Testing

Install dev dependencies (pytest, httpx, requests) and run tests **from `backend/`**:

```bash
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd backend
..\.venv\Scripts\python.exe -m pytest tests\ -v
```

Тесты используют **SQLite `:memory:`** и переменную окружения **`TESTING=1`** (ставится в `tests/conftest.py` до импорта приложения), без отдельного файла БД.

Быстрая ручная проверка API (нужен запущенный backend и совпадающий `ADMIN_API_KEY` в `.env`):

```bash
# из корня репозитория, после: cd backend && uvicorn main:app --reload
python test_quick.py
```

Опционально: `QUICK_TEST_BASE_URL`, `ADMIN_API_KEY` для скрипта. Для стека Docker: `QUICK_TEST_BASE_URL=http://127.0.0.1:8119`.

## Frontend + backend (локально)

Откройте фронт через **HTTP** (не `file://`), чтобы CORS и запросы к API работали предсказуемо.

**Терминал 1 — backend**

```bash
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Терминал 2 — статика frontend**

```bash
python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

В браузере: [http://127.0.0.1:8080](http://127.0.0.1:8080) — в `frontend/index.html` задан `API_BASE_URL` на `http://127.0.0.1:8000`.

Если backend недоступен, приложение переключается на **локальный режим** (localStorage) и показывает уведомление.

## Deployment (идеи)

| Слой | Вариант |
|------|---------|
| Frontend | Статический хостинг (например **Vercel**, **Netlify**, GitHub Pages) |
| Backend | **Render**, **Railway**, **Fly.io** — контейнер из `backend/Dockerfile` |
| БД | Сейчас **SQLite** (прототип); в production обычно **PostgreSQL** + миграции (Alembic) |

## Конфигурация `.env`

В **корне** репозитория скопируйте `.env.example` → `.env` (файл `.env` в `.gitignore`):

```
SECRET_KEY=dev-secret-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./data/moment.db
ADMIN_API_KEY=dev-admin-key-change-me
```

Значение `ADMIN_API_KEY` должно совпадать с заголовком `X-Admin-Key` при вызове `POST /api/event` и с тем, что использует `test_quick.py` (по умолчанию `dev-admin-key-change-me`).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login, returns JWT |
| POST | /api/prediction | Submit prediction (Bearer JWT) |
| GET | /api/leaderboard | Top 10 players |
| GET | /api/predictions/{user_id} | User history (own id only, JWT) |
| POST | /api/event | Confirm real event (`X-Admin-Key`) |
| GET | /api/stats | Global stats |
| GET | / | Краткая информация и ссылки на документацию |
| GET | /health | Health check (no rate limit) |

Rate limit: **10 requests/minute per IP** on each limited route.

Admin: send header `X-Admin-Key` equal to `ADMIN_API_KEY` from `.env`.

## Tech Stack

- Frontend: HTML/CSS/JS (Google AI Studio)
- Backend: Python 3.12, FastAPI, SQLAlchemy, bcrypt, JWT (python-jose)
- Database: SQLite (prototype)
- DevOps: Docker, Docker Compose

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Author

Dmitry Shamaraev | AI Engineer  
Telegram: [@turmerig](https://t.me/turmerig) | GitHub: [dn0sh](https://github.com/dn0sh)
