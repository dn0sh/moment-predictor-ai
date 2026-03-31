# 📋 Примечания по развёртыванию (Deployment Notes)

## 🗂️ Структура проекта

### Изначальная архитектура (локальная разработка)

```
moment-predictor-ai/
├── frontend/
│   ├── index.html
│   ├── videos.config.js
│   └── api-config.js
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker/
│   ├── docker-compose.yml
│   └── nginx/
├── docs/
│   └── ARCHITECTURE.md
├── .env.example
├── .gitignore
└── README.md
```

### Текущая структура (для GitHub Pages)

```
moment-predictor-ai/
├── index.html              ← Перемещён из frontend/
├── videos.config.js        ← Перемещён из frontend/
├── api-config.js           ← Перемещён из frontend/
├── backend/                ← Без изменений
├── docker/                 ← Без изменений
├── docs/                   ← Без изменений
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚠️ Почему файлы фронтенда в корне?

### Проблема GitHub Pages

GitHub Pages имеет ограничение на публикацию статических сайтов:

| Опция | Проблема |
|-------|----------|
| `/(root)` | Публикует **только корень** репозитория |
| `/docs` | Публикует **только папку docs/** |
| Custom branch | Требует отдельной ветки (gh-pages) |

**Наш выбор:** `/(root)` — чтобы не дублировать файлы и не усложнять workflow.

---

## 🔄 Для локальной разработки

Если вы клонировали репозиторий для локальной разработки:

### Вариант A: Использовать как есть (файлы в корне)

```bash
# Запустить фронтенд (из корня проекта)
python -m http.server 8080

# Открыть http://127.0.0.1:8080
```

### Вариант B: Вернуть структуру frontend/ (опционально)

```bash
# Создать папку frontend
mkdir frontend

# Переместить файлы
move index.html frontend/
move videos.config.js frontend/
move api-config.js frontend/

# Запустить
python -m http.server 8080 --directory frontend
```

**Для production на GitHub Pages** — вернуть файлы в корень перед деплоем.

---

## 🚀 Альтернативные варианты деплоя

### Vercel (рекомендуется для production)

Vercel поддерживает публикацию из подпапок:

```json
// vercel.json
{
  "buildCommand": "echo 'No build needed'",
  "outputDirectory": "frontend",
  "routes": [
    { "src": "/api/(.*)", "dest": "https://your-api.onrender.com/api/$1" }
  ]
}
```

**Преимущества:**
- ✅ Файлы могут оставаться в `frontend/`
- ✅ Автоматический HTTPS
- ✅ Preview деплои для pull request'ов
- ✅ Интеграция с GitHub

### Netlify

Аналогично Vercel — поддерживает публикацию из подпапок.

### Docker Compose (локально)

```bash
docker compose -f docker/docker-compose.yml up --build
```

Открыть: http://127.0.0.1:8118/

**Преимущества:**
- ✅ Полная изоляция
- ✅ Backend + Frontend вместе
- ✅ SQLite в томе (персистентность)

---

## 📊 Сравнение вариантов

| Параметр | GitHub Pages | Vercel | Docker |
|----------|--------------|--------|--------|
| **Структура** | Файлы в корне | frontend/ | frontend/ |
| **HTTPS** | ✅ Да | ✅ Да | ⚠️ Локально |
| **Backend API** | ❌ Отдельно | ✅ Прокси | ✅ Включён |
| **Сложность** | Низкая | Низкая | Средняя |
| **Для демо** | ✅ Отлично | ✅ Отлично | ✅ Локально |

---

## 🎯 Вывод

Перемещение файлов фронтенда в корень — **временное решение для GitHub Pages**, не влияющее на архитектуру проекта.

**Для production рекомендуется:**
1. Vercel (фронтенд) + Render/Railway (бэкенд)
2. Или Docker Compose на VPS
