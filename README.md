# prodev-landing

Лендинг студии prodev.team: FastAPI + SQLite (тексты в БД, админка) и React + Vite SPA.

## Быстрый старт (Docker)

```bash
cp .env.example .env   # задайте ADMIN_PASSWORD и SECRET_KEY
docker compose up -d --build
# лендинг:  http://localhost:8000
# админка:  http://localhost:8000/admin
```

## Разработка

```bash
# бэкенд
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload

# фронтенд (в другом терминале)
cd frontend && npm install && npm run dev   # http://localhost:5173, /api проксируется на :8000
```

## Как это устроено

- Все тексты лендинга (RU/EN) лежат в SQLite и редактируются через `/admin`.
- Начальное наполнение — `shared/seed_content.json`; он же вшит во фронт как
  фоллбэк на случай недоступного API.
- Один Docker-контейнер: FastAPI раздаёт и API, и собранную SPA.
