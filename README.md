# atrice landing

Лендинг студии atrice: FastAPI + SQLite (тексты в БД, админка) и React + Vite SPA.

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

## Деплой

Прод: https://alexander.puzh.dev.hlab.kz (nginx + Let's Encrypt, приложение слушает
только 127.0.0.1:8000; пользователь `deploy`, каталог `~/prodev-landing`).
Каждый пуш в `main` после зеленого CI автоматически деплоится на VPS: GitHub Actions
заходит по SSH и выполняет `git pull && docker compose up -d --build`.
Секреты: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` в настройках репозитория.
Админка доступна только с IP из `ADMIN_ALLOWED_IPS` (см. `.env.example`).

## Как это устроено

- Все тексты лендинга (RU/EN) лежат в SQLite и редактируются через `/admin`.
- Начальное наполнение - `shared/seed_content.json`; он же вшит во фронт как
  фоллбэк на случай недоступного API.
- Миграции данных (`backend/app/migrations.py`) применяются на старте,
  каждая один раз; применённые фиксируются в таблице `applied_migrations`.
- Один Docker-контейнер: FastAPI раздает и API, и собранную SPA.
