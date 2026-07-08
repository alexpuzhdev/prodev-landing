# atrice landing

Лендинг студии atrice: FastAPI + SQLite (тексты в БД, админка), React + Vite SPA
и Telegram-бот на aiogram (меню, портфолио, приём заявок).

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

Прод: https://atrice.ru (nginx + Let's Encrypt, приложение слушает
только 127.0.0.1:8000; пользователь `deploy`, каталог `~/prodev-landing`).
www.atrice.ru и старый hostname сервера редиректят на atrice.ru.
Каждый пуш в `main` после зеленого CI автоматически деплоится на VPS: GitHub Actions
заходит по SSH и выполняет `git pull && docker compose up -d --build`.
Секреты: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` в настройках репозитория.
Админка доступна только с IP из `ADMIN_ALLOWED_IPS` (см. `.env.example`).

## Telegram-бот

`bot/` - отдельный сервис на aiogram 3 (long polling), поднимается вместе с
приложением через docker-compose. Меню: портфолио, услуги, заявка, о студии.
Тексты бота и карточки портфолио правятся в `/admin`. Заявки уходят владельцу
в личку и в базу (раздел "Заявки" в админке).

Env бота (в общем `.env`): `BOT_TOKEN` (от @BotFather), `OWNER_CHAT_ID`
(chat id владельца - узнать: отправить боту сообщение и посмотреть
`https://api.telegram.org/bot<TOKEN>/getUpdates`), `SERVICE_TOKEN` (общий с
бэкендом секрет для `POST /api/leads`). `TG_PROXY` нужен только для локального
запуска за корпоративным egress; на проде пустой.

## Как это устроено

- Все тексты лендинга и бота (RU/EN) лежат в SQLite и редактируются через `/admin`.
- Начальное наполнение - `shared/seed_content.json`; он же вшит во фронт как
  фоллбэк на случай недоступного API.
- Миграции данных (`backend/app/migrations.py`) применяются на старте,
  каждая один раз; применённые фиксируются в таблице `applied_migrations`.
- Приложение: один Docker-контейнер (FastAPI раздает API и собранную SPA).
  Бот - второй контейнер, ходит в бэкенд по внутренней сети compose.
