# prodev-landing — дизайн мини-проекта

Дата: 2026-07-07
Статус: одобрено пользователем

## Цель

Превратить статический лендинг prodev.team (`index.html`, реализация макета
«Developer Landing v2» из Claude Design) в полноценный мини-проект: бэкенд
с БД, из которой лендинг берёт все тексты, и админка для их редактирования.
Репозиторий на GitHub, Docker-инфраструктура, CI/CD.

## Решения (зафиксированы с пользователем)

| Вопрос | Решение |
|---|---|
| Бэкенд | Python + FastAPI |
| БД | SQLite (через SQLAlchemy; миграция на Postgres возможна позже) |
| Админка | Своя страница `/admin` (не автогенерируемая) |
| Фронтенд | React + Vite + TypeScript (SPA), вёрстка переносится из index.html один в один |
| Инфраструктура | Docker + docker-compose, GitHub Actions CI, автодеплой на VPS |
| Репозиторий | Публичный `alexpuzhdev/prodev-landing` |

## Структура репозитория (монорепо)

```
prodev-landing/
├─ backend/               # FastAPI + SQLAlchemy + SQLite
│  ├─ app/
│  │  ├─ main.py          # приложение, роуты, раздача статики фронта
│  │  ├─ models.py        # модель Content
│  │  ├─ auth.py          # логин по паролю, подписанная cookie-сессия
│  │  ├─ seed.py          # сидирование пустой БД из seed_content.json
│  │  └─ seed_content.json
│  ├─ tests/              # pytest
│  └─ pyproject.toml      # зависимости + ruff
├─ frontend/              # React + Vite + TypeScript
│  ├─ src/
│  │  ├─ sections/        # Header, Hero, Terminal, About, Services, Stack, Cta, Footer, ScrollSquare
│  │  ├─ admin/           # страница /admin: логин + таблица текстов
│  │  ├─ content.ts       # загрузка текстов с API, фоллбэк на вшитые
│  │  ├─ defaults.ts      # вшитая копия seed-текстов (фоллбэк)
│  │  └─ styles.css       # CSS из index.html без изменений
│  └─ vite.config.ts      # dev-proxy /api → backend
├─ Dockerfile             # multi-stage: node-сборка фронта → python-образ
├─ docker-compose.yml     # app + volume ./data для SQLite
├─ .env.example           # ADMIN_PASSWORD, SECRET_KEY
├─ .github/workflows/
│  ├─ ci.yml              # ruff, pytest, tsc, vite build, docker build
│  └─ deploy.yml          # SSH-деплой на VPS по пушу в main
└─ docs/superpowers/specs/  # этот документ
```

## Данные и API

Таблица `content`:

| Поле | Тип | Назначение |
|---|---|---|
| key | str, PK | машинный ключ (например `heroTitle`) |
| ru | text | текст на русском |
| en | text | текст на английском |
| label | str | человекочитаемое название для админки |
| section | str | группа в админке (Шапка, Hero, Услуги, …) |
| updated_at | datetime | время последнего изменения |

Содержимое: все строки локализации текущего лендинга (шапка, hero, услуги,
стек, CTA, футер), переводимые строки терминала (`ok`/`info`-строки) и
телеграм-хэндл (`telegramHandle`, ru == en). Команды терминала
(`git clone…`, `npm run build`, …) остаются в коде фронтенда — это часть
анимации, не контент.

Эндпоинты:

- `GET /api/content` → `{key: {ru, en}}` — все тексты одним запросом,
  переключение языка на фронте без повторных запросов.
- `POST /api/auth/login` `{password}` — сверка с env `ADMIN_PASSWORD`;
  при успехе выставляется подписанная (itsdangerous, ключ `SECRET_KEY`)
  httponly-cookie. `POST /api/auth/logout` — сброс.
- `PUT /api/content/{key}` `{ru, en}` — только с валидной сессией, иначе 401.

При старте: если таблица пуста — сидирование из `seed_content.json`.

## Фронтенд

React Router, два роута: `/` (лендинг) и `/admin`.

Лендинг: секции — компоненты, дизайн-система (цвета `#f0eee6`/`#141413`/`#d97757`,
шрифты Golos Text / Source Serif 4 / моноширинный стек, радиусы, анимации
fadeUp/floatY/spinSlow, терминал с посимвольной печатью, скролл-квадратик
540°) переносится из `index.html` без визуальных изменений. Тексты загружаются
через `GET /api/content` при монтировании; до ответа и при ошибке API
используются вшитые тексты из `defaults.ts` — страница никогда не пустая.
Язык RU/EN — состояние + localStorage (`prodev_lang`), как сейчас.
`prefers-reduced-motion` отключает анимации.

Админка `/admin`: форма логина (пароль) → таблица всех текстов,
сгруппированная по `section`, колонки RU и EN редактируются рядом,
сохранение построчно (PUT), индикация успеха/ошибки. Никаких сторонних
UI-библиотек — та же дизайн-система, что у лендинга.

## Инфраструктура

Один контейнер: multi-stage Dockerfile — `node:22` собирает `frontend/dist`,
итоговый образ `python:3.12-slim` с FastAPI, который раздаёт `/api` и статику
SPA (включая fallback на `index.html` для клиентского роутинга `/admin`).
SQLite-файл — в volume `./data`. Конфигурация через env:
`ADMIN_PASSWORD`, `SECRET_KEY` (пример — в `.env.example`).

CI (`ci.yml`, push + PR): ruff и pytest для бэка; `tsc --noEmit` и
`vite build` для фронта; сборка Docker-образа.

CD (`deploy.yml`, push в main, после CI): SSH на VPS →
`git pull && docker compose up -d --build`. Требует секретов
`VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` — добавляет пользователь, до этого
воркфлоу «заряжен», но не активен (guard: пропуск, если секреты не заданы).

## Тесты

Backend (pytest, httpx TestClient, временная SQLite):
- GET /api/content возвращает сидированные тексты в формате `{key: {ru, en}}`;
- логин с верным паролем ставит cookie, с неверным — 401;
- PUT /api/content/{key} без сессии — 401, с сессией — обновляет и
  возвращает новое значение; несуществующий ключ — 404.

Frontend: `tsc --noEmit` в CI; unit-тест (vitest) на фоллбэк контента при
недоступном API.

## Обработка ошибок

- API недоступен на лендинге → тихий фоллбэк на вшитые тексты.
- Ошибка сохранения в админке → видимое сообщение у строки, данные не теряются.
- 401 в админке → возврат к форме логина.

## Вне скоупа / отложено

- Секреты VPS и первый прод-деплой — на стороне пользователя.
- Реальные ссылки GitHub/LinkedIn в футере (сейчас `#top`, как в макете) и
  реальный телеграм-хэндл — правятся через админку после запуска.
- Postgres, мультиязычность сверх RU/EN, роли пользователей — не делаем.
