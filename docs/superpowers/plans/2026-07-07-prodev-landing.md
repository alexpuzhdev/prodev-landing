# prodev-landing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Превратить статический лендинг prodev.team в мини-проект: FastAPI-бэкенд с текстами в SQLite и админкой, React+Vite SPA, Docker, CI/CD, публичная репа GitHub.

**Architecture:** Монорепо. Один FastAPI-процесс раздаёт `/api` и собранную SPA. Тексты — единый JSON-сид (`shared/seed_content.json`), из него сидируется БД и берётся фоллбэк фронта. Админка — роут SPA, авторизация — подписанная cookie.

**Tech Stack:** Python 3.10+/FastAPI/SQLAlchemy/SQLite/itsdangerous; React 18 + Vite + TypeScript + react-router-dom; pytest, vitest, ruff; Docker multi-stage; GitHub Actions.

**Спека:** `docs/superpowers/specs/2026-07-07-prodev-landing-design.md` — источник требований.

## Global Constraints

- Дизайн лендинга не меняется: эталон — `index.html` в корне репо (фон `#f0eee6`, чернила `#141413`, акцент `#d97757`, шрифты Golos Text / Source Serif 4 / `ui-monospace`-стек, кнопки radius 10px, терминал 13.5px/1.75, скролл-квадратик 540°).
- Тексты в сид переносятся ДОСЛОВНО из `index.html` (словарь `I18N`, футер, терминал).
- Локальный Python — 3.10, в Docker — 3.12: код совместим с 3.10 (без синтаксиса 3.11+).
- Node 22, реестр npm; никаких UI-библиотек (только react, react-dom, react-router-dom).
- Сообщения пользователю в админке — по-русски.
- Ключ localStorage языка — `prodev_lang` (совместимость со старой страницей).
- Все команды выполняются из корня репо, если не сказано иное.
- Коммиты — частые, после каждой задачи; сообщение оканчивается `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

---

### Task 1: Скаффолдинг репозитория, сид-контент, репа на GitHub

**Files:**
- Create: `.gitignore`, `README.md`, `.env.example`, `shared/seed_content.json`

**Interfaces:**
- Produces: `shared/seed_content.json` — объект `{key: {ru, en, label, section}}`; его читают backend-сид (Task 2) и фронт-фоллбэк (Task 5). Ключи перечислены ниже и менять их нельзя.

- [ ] **Step 1: Создать .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.ruff_cache/
*.egg-info/

# Node
node_modules/
frontend/dist/

# Data & env
data/
*.db
.env

# IDE / OS
.idea/
.vscode/
.DS_Store

# Playwright artifacts
.playwright-mcp/
```

- [ ] **Step 2: Создать README.md (черновик, финалится в Task 10)**

```markdown
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
```

- [ ] **Step 3: Создать .env.example**

```bash
# Пароль входа в админку /admin
ADMIN_PASSWORD=change-me
# Ключ подписи cookie-сессии (openssl rand -hex 32)
SECRET_KEY=change-me-too
```

- [ ] **Step 4: Создать shared/seed_content.json**

Полное содержимое (тексты дословно из `index.html`):

```json
{
  "brandName":     {"ru": "prodev.team", "en": "prodev.team", "label": "Название студии", "section": "Шапка"},
  "navAbout":      {"ru": "О команде", "en": "About", "label": "Меню: о команде", "section": "Шапка"},
  "navServices":   {"ru": "Услуги", "en": "Services", "label": "Меню: услуги", "section": "Шапка"},
  "navStack":      {"ru": "Стек", "en": "Stack", "label": "Меню: стек", "section": "Шапка"},
  "ctaHeader":     {"ru": "Написать в Telegram", "en": "Message on Telegram", "label": "Кнопка Telegram (шапка/CTA/футер)", "section": "Шапка"},

  "kicker":        {"ru": "Студия full-stack разработки · работаем удалённо", "en": "Full-stack development studio · fully remote", "label": "Подзаголовок над заголовком", "section": "Hero"},
  "heroTitle":     {"ru": "Цифровые продукты, которые запускаются в срок.", "en": "Digital products that ship on time.", "label": "Главный заголовок", "section": "Hero"},
  "heroText":      {"ru": "Команда инженеров и дизайнеров: проектируем, разрабатываем и запускаем веб-приложения, лендинги и MVP. Полный цикл — от идеи до продакшена.", "en": "A team of engineers and designers: we plan, build and launch web apps, landing pages and MVPs. Full cycle — from idea to production.", "label": "Текст рядом с заголовком", "section": "Hero"},
  "ctaDiscuss":    {"ru": "Обсудить проект", "en": "Discuss a project", "label": "Кнопка «обсудить»", "section": "Hero"},
  "ctaServices":   {"ru": "Смотреть услуги", "en": "View services", "label": "Кнопка «услуги»", "section": "Hero"},

  "termTitle":     {"ru": "prodev — deploy", "en": "prodev — deploy", "label": "Заголовок окна терминала", "section": "Терминал"},
  "termScope":     {"ru": "скоуп и оценка — 1 день", "en": "scope & estimate — 1 day", "label": "Строка: скоуп", "section": "Терминал"},
  "termStack1":    {"ru": "frontend · react + typescript", "en": "frontend · react + typescript", "label": "Строка: фронтенд", "section": "Терминал"},
  "termStack2":    {"ru": "backend · node + postgres", "en": "backend · node + postgres", "label": "Строка: бэкенд", "section": "Терминал"},
  "termTests":     {"ru": "тесты пройдены (128/128)", "en": "tests passed (128/128)", "label": "Строка: тесты", "section": "Терминал"},
  "termDeploying": {"ru": "деплой в продакшен…", "en": "deploying to production…", "label": "Строка: деплой", "section": "Терминал"},
  "termLive":      {"ru": "запущено: от идеи до продакшена за недели, не месяцы", "en": "live: from idea to production in weeks, not months", "label": "Строка: запущено", "section": "Терминал"},

  "aboutTitle":    {"ru": "О команде", "en": "About the team", "label": "Заголовок секции", "section": "О команде"},
  "aboutP1":       {"ru": "Мы — компактная команда разработчиков и дизайнера. Берём проект целиком и ведём его до продакшена: без посредников, вы общаетесь напрямую с теми, кто делает продукт.", "en": "We're a compact team of developers and a designer. We take a project end to end and ship it to production — no middlemen, you talk directly to the people building your product.", "label": "Абзац 1", "section": "О команде"},
  "aboutP2":       {"ru": "Работаем итерациями: сначала версия, которую можно показать пользователям, затем развитие на основе реальных данных. Фиксируем сроки и объём до старта — и придерживаемся их.", "en": "We work in iterations: first a version you can put in front of users, then improvements driven by real data. Scope and timeline are fixed before we start — and we stick to them.", "label": "Абзац 2", "section": "О команде"},

  "servicesTitle": {"ru": "Услуги", "en": "Services", "label": "Заголовок секции", "section": "Услуги"},
  "svc1Title":     {"ru": "MVP под ключ", "en": "Turnkey MVP", "label": "Карточка 1: заголовок", "section": "Услуги"},
  "svc1Text":      {"ru": "От идеи до продукта, который можно показывать инвесторам и первым пользователям. Архитектура, разработка, запуск — в согласованные сроки.", "en": "From idea to a product you can show investors and first users. Architecture, development, launch — within an agreed timeline.", "label": "Карточка 1: текст", "section": "Услуги"},
  "svc2Title":     {"ru": "Лендинги и сайты", "en": "Landing pages & sites", "label": "Карточка 2: заголовок", "section": "Услуги"},
  "svc2Text":      {"ru": "Страницы, которые доносят оффер и конвертируют: запуск продукта, услуга, портфолио. Вёрстка, формы, аналитика — всё включено.", "en": "Pages that communicate the offer and convert: product launches, services, portfolios. Markup, forms, analytics — all included.", "label": "Карточка 2: текст", "section": "Услуги"},
  "svc3Title":     {"ru": "Веб-приложения", "en": "Web applications", "label": "Карточка 3: заголовок", "section": "Услуги"},
  "svc3Text":      {"ru": "Личные кабинеты, админки, внутренние инструменты. Фронтенд и бэкенд из одних рук — с авторизацией, базой данных и интеграциями.", "en": "Dashboards, admin panels, internal tools. Frontend and backend from one team — with auth, a database and integrations.", "label": "Карточка 3: текст", "section": "Услуги"},
  "svc4Title":     {"ru": "Поддержка и развитие", "en": "Support & growth", "label": "Карточка 4: заголовок", "section": "Услуги"},
  "svc4Text":      {"ru": "Возьмём существующий проект: исправим баги, ускорим, добавим функциональность. Аудит кода перед стартом — бесплатно.", "en": "We'll take over an existing project: fix bugs, improve performance, add features. Code audit before we start — free.", "label": "Карточка 4: текст", "section": "Услуги"},

  "stackTitle":      {"ru": "Стек технологий", "en": "Tech stack", "label": "Заголовок секции", "section": "Стек"},
  "stackFront":      {"ru": "Фронтенд", "en": "Frontend", "label": "Колонка 1: заголовок", "section": "Стек"},
  "stackFrontItems": {"ru": "TypeScript · React · Next.js · Tailwind CSS", "en": "TypeScript · React · Next.js · Tailwind CSS", "label": "Колонка 1: список", "section": "Стек"},
  "stackBack":       {"ru": "Бэкенд", "en": "Backend", "label": "Колонка 2: заголовок", "section": "Стек"},
  "stackBackItems":  {"ru": "Node.js · PostgreSQL · Redis · REST / GraphQL", "en": "Node.js · PostgreSQL · Redis · REST / GraphQL", "label": "Колонка 2: список", "section": "Стек"},
  "stackInfra":      {"ru": "Инфраструктура", "en": "Infrastructure", "label": "Колонка 3: заголовок", "section": "Стек"},
  "stackInfraItems": {"ru": "Docker · CI/CD · Vercel · VPS", "en": "Docker · CI/CD · Vercel · VPS", "label": "Колонка 3: список", "section": "Стек"},

  "ctaTitle": {"ru": "Расскажите о задаче", "en": "Tell us about your project", "label": "Заголовок CTA", "section": "CTA"},
  "ctaText":  {"ru": "Опишите её в двух словах — вернёмся в течение дня с оценкой сроков и стоимости.", "en": "Describe it in a couple of sentences — we'll get back within a day with a time and cost estimate.", "label": "Текст CTA", "section": "CTA"},

  "footCompany":   {"ru": "Компания", "en": "Company", "label": "Колонка «Компания»", "section": "Футер"},
  "footTop":       {"ru": "Наверх", "en": "Back to top", "label": "Ссылка «наверх»", "section": "Футер"},
  "footContact":   {"ru": "Контакты", "en": "Contact", "label": "Колонка «Контакты»", "section": "Футер"},
  "footReply":     {"ru": "Отвечаем в течение дня", "en": "We reply within a day", "label": "Строка про ответ", "section": "Футер"},
  "footCopyright": {"ru": "© 2026 prodev.team", "en": "© 2026 prodev.team", "label": "Копирайт", "section": "Футер"},

  "telegramHandle": {"ru": "your_handle", "en": "your_handle", "label": "Telegram-хэндл (без @)", "section": "Контакты"}
}
```

- [ ] **Step 5: Проверить валидность JSON**

Run: `python3 -c "import json; d=json.load(open('shared/seed_content.json')); print(len(d), 'keys')"`
Expected: `42 keys`

- [ ] **Step 6: Коммит**

```bash
git add .gitignore README.md .env.example shared/
git commit -m "chore: scaffold repo, add seed content and env example"
```

- [ ] **Step 7: Создать публичную репу на GitHub и запушить**

Сначала проверить авторизацию: `gh auth status` — должно быть `Logged in`. Если токен невалиден — СТОП, попросить пользователя выполнить `gh auth login -h github.com`.

```bash
gh repo create alexpuzhdev/prodev-landing --public --source=. --remote=origin --push
```

Expected: репа создана, ветка `main` запушена. Проверка: `gh repo view alexpuzhdev/prodev-landing --json url -q .url`.

---

### Task 2: Backend — каркас, модель Content, GET /api/content

**Files:**
- Create: `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/app/models.py`, `backend/app/db.py`, `backend/app/seed.py`, `backend/app/content.py`, `backend/app/main.py`, `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/test_content.py`

**Interfaces:**
- Consumes: `shared/seed_content.json` (Task 1).
- Produces: `create_app() -> FastAPI` в `app.main` (env: `DB_PATH`, `SEED_PATH`, `ADMIN_PASSWORD`, `SECRET_KEY`, `STATIC_DIR`); `GET /api/content` → `{key: {ru, en, label, section}}`; модель `Content(key, ru, en, label, section, updated_at)`; зависимость `get_db`; `app.state.sessionmaker`, `app.state.admin_password`, `app.state.secret_key`.

- [ ] **Step 1: Создать backend/pyproject.toml**

```toml
[project]
name = "prodev-backend"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0",
    "itsdangerous>=2.2",
]

[project.optional-dependencies]
dev = ["pytest>=8", "httpx>=0.27", "ruff>=0.6"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["app"]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Установить зависимости**

Run: `cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`
Expected: успешная установка. Дальше все backend-команды — через `backend/.venv/bin/…`.

- [ ] **Step 3: Написать падающий тест на GET /api/content**

`backend/tests/conftest.py`:

```python
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    os.environ["ADMIN_PASSWORD"] = "test-password"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ.pop("STATIC_DIR", None)
    from app.main import create_app

    with TestClient(create_app()) as c:
        yield c
```

`backend/tests/test_content.py`:

```python
def test_get_content_returns_seeded_texts(client):
    resp = client.get("/api/content")
    assert resp.status_code == 200
    data = resp.json()
    assert data["heroTitle"]["ru"] == "Цифровые продукты, которые запускаются в срок."
    assert data["heroTitle"]["en"] == "Digital products that ship on time."
    assert data["heroTitle"]["section"] == "Hero"
    assert len(data) >= 40
```

Пустые `backend/app/__init__.py` и `backend/tests/__init__.py`.

- [ ] **Step 4: Убедиться, что тест падает**

Run: `cd backend && .venv/bin/pytest tests/test_content.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'app.main'`)

- [ ] **Step 5: Реализовать модель, БД, сид и роут**

`backend/app/models.py`:

```python
from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Content(Base):
    __tablename__ = "content"

    key: Mapped[str] = mapped_column(primary_key=True)
    ru: Mapped[str] = mapped_column(default="")
    en: Mapped[str] = mapped_column(default="")
    label: Mapped[str] = mapped_column(default="")
    section: Mapped[str] = mapped_column(default="")
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)
```

`backend/app/db.py`:

```python
from fastapi import Request


def get_db(request: Request):
    session = request.app.state.sessionmaker()
    try:
        yield session
    finally:
        session.close()
```

`backend/app/seed.py`:

```python
import json
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Content


def seed_if_empty(session: Session, seed_path: Path) -> int:
    if session.query(Content).count() > 0:
        return 0
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    for key, row in data.items():
        session.add(
            Content(
                key=key,
                ru=row["ru"],
                en=row["en"],
                label=row.get("label", key),
                section=row.get("section", ""),
            )
        )
    session.commit()
    return len(data)
```

`backend/app/content.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import Content

router = APIRouter(prefix="/api/content")


@router.get("")
def get_content(db: Session = Depends(get_db)):
    rows = db.query(Content).all()
    return {
        r.key: {"ru": r.ru, "en": r.en, "label": r.label, "section": r.section} for r in rows
    }
```

`backend/app/main.py`:

```python
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import content
from .models import Base
from .seed import seed_if_empty

BACKEND_DIR = Path(__file__).resolve().parent.parent


def create_app() -> FastAPI:
    db_path = Path(os.environ.get("DB_PATH", BACKEND_DIR / "data" / "content.db"))
    seed_path = Path(
        os.environ.get("SEED_PATH", BACKEND_DIR.parent / "shared" / "seed_content.json")
    )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        with app.state.sessionmaker() as session:
            seed_if_empty(session, seed_path)
        yield

    app = FastAPI(title="prodev-landing", lifespan=lifespan)
    app.state.sessionmaker = sessionmaker(bind=engine)
    app.state.admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    app.state.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    app.include_router(content.router)
    return app


app = create_app()
```

- [ ] **Step 6: Прогнать тест**

Run: `cd backend && .venv/bin/pytest tests/test_content.py -v`
Expected: PASS

- [ ] **Step 7: Линт и коммит**

```bash
cd backend && .venv/bin/ruff check . && cd ..
git add backend/
git commit -m "feat(backend): content model, seeding and GET /api/content"
```

---

### Task 3: Backend — авторизация (login/logout/me, cookie-сессия)

**Files:**
- Create: `backend/app/auth.py`, `backend/tests/test_auth.py`
- Modify: `backend/app/main.py` (подключить роутер)

**Interfaces:**
- Consumes: `app.state.admin_password`, `app.state.secret_key` (Task 2).
- Produces: `POST /api/auth/login {password}` → 200 + cookie `prodev_session` | 401; `POST /api/auth/logout`; `GET /api/auth/me` → 200 `{ok: true}` | 401; зависимость `require_admin(request)` для Task 4.

- [ ] **Step 1: Написать падающие тесты**

`backend/tests/test_auth.py`:

```python
def test_login_wrong_password_401(client):
    resp = client.post("/api/auth/login", json={"password": "wrong"})
    assert resp.status_code == 401


def test_login_ok_sets_cookie_and_me_works(client):
    assert client.get("/api/auth/me").status_code == 401
    resp = client.post("/api/auth/login", json={"password": "test-password"})
    assert resp.status_code == 200
    assert "prodev_session" in resp.cookies
    assert client.get("/api/auth/me").status_code == 200


def test_logout_clears_session(client):
    client.post("/api/auth/login", json={"password": "test-password"})
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401
```

- [ ] **Step 2: Убедиться, что тесты падают**

Run: `cd backend && .venv/bin/pytest tests/test_auth.py -v`
Expected: FAIL (404 на /api/auth/login)

- [ ] **Step 3: Реализовать auth.py и подключить роутер**

`backend/app/auth.py`:

```python
from fastapi import APIRouter, HTTPException, Request, Response
from itsdangerous import BadSignature, TimestampSigner
from pydantic import BaseModel

COOKIE_NAME = "prodev_session"
MAX_AGE = 60 * 60 * 24  # сутки

router = APIRouter(prefix="/api/auth")


class LoginBody(BaseModel):
    password: str


def _signer(request: Request) -> TimestampSigner:
    return TimestampSigner(request.app.state.secret_key)


def require_admin(request: Request) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Требуется вход")
    try:
        _signer(request).unsign(token, max_age=MAX_AGE)
    except BadSignature:
        raise HTTPException(status_code=401, detail="Сессия недействительна")


@router.post("/login")
def login(body: LoginBody, request: Request, response: Response):
    if body.password != request.app.state.admin_password:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    token = _signer(request).sign("admin").decode()
    response.set_cookie(
        COOKIE_NAME, token, max_age=MAX_AGE, httponly=True, samesite="lax"
    )
    return {"ok": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    require_admin(request)
    return {"ok": True}
```

В `backend/app/main.py`: заменить `from . import content` на `from . import auth, content` и после `app.include_router(content.router)` добавить строку `app.include_router(auth.router)`.

- [ ] **Step 4: Прогнать тесты**

Run: `cd backend && .venv/bin/pytest -v`
Expected: все PASS

- [ ] **Step 5: Линт и коммит**

```bash
cd backend && .venv/bin/ruff check . && cd ..
git add backend/
git commit -m "feat(backend): admin auth with signed cookie session"
```

---

### Task 4: Backend — PUT /api/content/{key} (только для админа)

**Files:**
- Modify: `backend/app/content.py`
- Test: `backend/tests/test_content.py` (добавить тесты)

**Interfaces:**
- Consumes: `require_admin` (Task 3), `get_db`, модель `Content` (Task 2).
- Produces: `PUT /api/content/{key}` body `{ru: str, en: str}` → 200 `{key, ru, en}` | 401 без сессии | 404 неизвестный ключ. Это контракт для админки (Task 8).

- [ ] **Step 1: Добавить падающие тесты в test_content.py**

```python
def test_put_content_requires_auth(client):
    resp = client.put("/api/content/heroTitle", json={"ru": "x", "en": "y"})
    assert resp.status_code == 401


def test_put_content_updates_value(client):
    client.post("/api/auth/login", json={"password": "test-password"})
    resp = client.put(
        "/api/content/heroTitle", json={"ru": "Новый заголовок", "en": "New title"}
    )
    assert resp.status_code == 200
    assert resp.json() == {"key": "heroTitle", "ru": "Новый заголовок", "en": "New title"}
    data = client.get("/api/content").json()
    assert data["heroTitle"]["ru"] == "Новый заголовок"


def test_put_unknown_key_404(client):
    client.post("/api/auth/login", json={"password": "test-password"})
    resp = client.put("/api/content/noSuchKey", json={"ru": "x", "en": "y"})
    assert resp.status_code == 404
```

- [ ] **Step 2: Убедиться, что тесты падают**

Run: `cd backend && .venv/bin/pytest tests/test_content.py -v`
Expected: 3 новых FAIL (405 Method Not Allowed), старый PASS

- [ ] **Step 3: Реализовать PUT**

`backend/app/content.py` — полная новая версия файла:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import require_admin
from .db import get_db
from .models import Content, utcnow

router = APIRouter(prefix="/api/content")


class ContentUpdate(BaseModel):
    ru: str
    en: str


@router.get("")
def get_content(db: Session = Depends(get_db)):
    rows = db.query(Content).all()
    return {
        r.key: {"ru": r.ru, "en": r.en, "label": r.label, "section": r.section} for r in rows
    }


@router.put("/{key}", dependencies=[Depends(require_admin)])
def update_content(key: str, body: ContentUpdate, db: Session = Depends(get_db)):
    row = db.get(Content, key)
    if row is None:
        raise HTTPException(status_code=404, detail="Ключ не найден")
    row.ru = body.ru
    row.en = body.en
    row.updated_at = utcnow()
    db.commit()
    return {"key": key, "ru": row.ru, "en": row.en}
```

- [ ] **Step 4: Прогнать все тесты**

Run: `cd backend && .venv/bin/pytest -v`
Expected: все PASS

- [ ] **Step 5: Линт и коммит**

```bash
cd backend && .venv/bin/ruff check . && cd ..
git add backend/
git commit -m "feat(backend): PUT /api/content/{key} guarded by admin session"
```

---

### Task 5: Frontend — скаффолд Vite, стили, контент-инфраструктура с фоллбэком

**Files:**
- Create: `frontend/` (Vite react-ts шаблон), `frontend/src/styles.css`, `frontend/src/content.tsx`, `frontend/src/content.test.ts`, `frontend/src/App.tsx` (замена), `frontend/src/main.tsx` (замена)
- Delete: `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/assets/react.svg`, `frontend/public/vite.svg`

**Interfaces:**
- Consumes: `shared/seed_content.json` (Task 1); `GET /api/content` (Task 2).
- Produces: `ContentProvider`, хук `useContent(): { lang: 'ru'|'en'; setLang(l): void; t(key: string): string; texts: ContentMap }`, `fetchContent(): Promise<ContentMap>`, `resolveTexts(remote: ContentMap | null): ContentMap`, `defaults: ContentMap` — используются всеми секциями (Task 6–7) и админкой (Task 8). Тип `ContentMap = Record<string, {ru: string; en: string; label?: string; section?: string}>`.

- [ ] **Step 1: Скаффолд Vite**

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install && npm install react-router-dom && npm install -D vitest
```

- [ ] **Step 2: Настроить vite.config.ts**

Полная замена `frontend/vite.config.ts`:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:8000' },
    fs: { allow: ['..'] },
  },
})
```

В `frontend/tsconfig.app.json` в `compilerOptions` добавить `"resolveJsonModule": true`.
В `frontend/package.json` в `scripts` добавить `"test": "vitest run"`.

- [ ] **Step 3: Перенести стили**

Создать `frontend/src/styles.css`: скопировать всё содержимое тега `<style>` из корневого `index.html` (от `:root {` до последнего `}` медиазапроса) БЕЗ изменений. Удалить `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/assets/react.svg`, `frontend/public/vite.svg`.

В `frontend/index.html` заменить `<title>` на `prodev.team — студия full-stack разработки`, добавить в `<head>` строки шрифтов и фавиконки из корневого `index.html`:

```html
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='7' fill='%23d97757'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

- [ ] **Step 4: Написать падающий тест на фоллбэк**

`frontend/src/content.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { defaults, resolveTexts } from './content'

describe('resolveTexts', () => {
  it('возвращает вшитые тексты, когда API недоступен', () => {
    expect(resolveTexts(null)).toEqual(defaults)
  })

  it('накладывает ответ API поверх вшитых', () => {
    const remote = { heroTitle: { ru: 'X', en: 'Y' } }
    const merged = resolveTexts(remote)
    expect(merged.heroTitle.ru).toBe('X')
    expect(merged.kicker.ru).toBe(defaults.kicker.ru)
  })

  it('пустой ответ API означает фоллбэк целиком', () => {
    expect(resolveTexts({})).toEqual(defaults)
  })
})
```

Run: `cd frontend && npm test`
Expected: FAIL (content.ts не существует)

- [ ] **Step 5: Реализовать content.tsx**

`frontend/src/content.tsx`:

```tsx
import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import seed from '../../shared/seed_content.json'

export type Lang = 'ru' | 'en'
export type ContentMap = Record<
  string,
  { ru: string; en: string; label?: string; section?: string }
>

export const defaults: ContentMap = seed as ContentMap

export async function fetchContent(): Promise<ContentMap> {
  const res = await fetch('/api/content')
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}

export function resolveTexts(remote: ContentMap | null): ContentMap {
  return remote && Object.keys(remote).length > 0 ? { ...defaults, ...remote } : defaults
}

type Ctx = {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string) => string
  texts: ContentMap
}

const ContentContext = createContext<Ctx | null>(null)

export function ContentProvider({ children }: { children: ReactNode }) {
  const [texts, setTexts] = useState<ContentMap>(defaults)
  const [lang, setLangState] = useState<Lang>(() =>
    localStorage.getItem('prodev_lang') === 'en' ? 'en' : 'ru',
  )

  useEffect(() => {
    fetchContent()
      .then((remote) => setTexts(resolveTexts(remote)))
      .catch(() => {})
  }, [])

  const setLang = (l: Lang) => {
    localStorage.setItem('prodev_lang', l)
    setLangState(l)
  }

  const t = (key: string) => texts[key]?.[lang] ?? defaults[key]?.[lang] ?? key

  return (
    <ContentContext.Provider value={{ lang, setLang, t, texts }}>
      {children}
    </ContentContext.Provider>
  )
}

export function useContent(): Ctx {
  const ctx = useContext(ContentContext)
  if (!ctx) throw new Error('useContent вне ContentProvider')
  return ctx
}
```

- [ ] **Step 6: Заменить App.tsx и main.tsx**

`frontend/src/main.tsx`:

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

`frontend/src/App.tsx` (лендинг-заглушка до Task 6):

```tsx
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ContentProvider, useContent } from './content'

function Landing() {
  const { t } = useContent()
  return <h1>{t('heroTitle')}</h1>
}

export default function App() {
  return (
    <BrowserRouter>
      <ContentProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
        </Routes>
      </ContentProvider>
    </BrowserRouter>
  )
}
```

- [ ] **Step 7: Проверить тесты, типы, сборку**

Run: `cd frontend && npm test && npx tsc --noEmit -p tsconfig.app.json && npm run build`
Expected: тесты PASS, ошибок типов нет, `dist/` собрался

- [ ] **Step 8: Коммит**

```bash
git add frontend/
git commit -m "feat(frontend): Vite scaffold, styles port, content provider with fallback"
```

---

### Task 6: Frontend — секции Header, Hero, Terminal, ScrollSquare

**Files:**
- Create: `frontend/src/sections/Header.tsx`, `frontend/src/sections/Hero.tsx`, `frontend/src/sections/Terminal.tsx`, `frontend/src/sections/ScrollSquare.tsx`, `frontend/src/sections/Landing.tsx`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `useContent()` (Task 5); CSS-классы из `styles.css`.
- Produces: компонент `Landing` (собирает все секции; About/Services/Stack/Cta/Footer добавятся в Task 7); хелпер `tgLink(t): string`; `terminalLines(t): {type: 'cmd'|'ok'|'info'; text: string}[]` (внутри Terminal.tsx).

- [ ] **Step 1: Header.tsx**

```tsx
import { useContent } from '../content'

export function tgLink(t: (k: string) => string): string {
  return 'https://t.me/' + t('telegramHandle')
}

export function Header() {
  const { t, lang, setLang } = useContent()
  return (
    <header className="site-header">
      <a href="#top" className="logo">
        <span className="logo-dot"></span>
        <span>{t('brandName')}</span>
      </a>
      <nav className="site-nav">
        <a href="#about">{t('navAbout')}</a>
        <a href="#services">{t('navServices')}</a>
        <a href="#stack">{t('navStack')}</a>
      </nav>
      <div className="header-actions">
        <div className="lang-switch" role="group" aria-label="Language">
          <button type="button" className={lang === 'ru' ? 'active' : ''} onClick={() => setLang('ru')}>
            RU
          </button>
          <button type="button" className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>
            EN
          </button>
        </div>
        <a className="btn btn-dark" href={tgLink(t)} target="_blank" rel="noopener">
          {t('ctaHeader')}
        </a>
      </div>
    </header>
  )
}
```

- [ ] **Step 2: Hero.tsx**

```tsx
import { useContent } from '../content'
import { tgLink } from './Header'

export function Hero() {
  const { t } = useContent()
  return (
    <section className="hero">
      <div className="hero-shape-ring" aria-hidden="true"></div>
      <div className="hero-shape-dot" aria-hidden="true"></div>
      <div className="hero-shape-square" aria-hidden="true"></div>
      <p className="hero-kicker">{t('kicker')}</p>
      <div className="hero-grid">
        <h1>{t('heroTitle')}</h1>
        <div className="hero-side">
          <p>{t('heroText')}</p>
          <div className="hero-cta">
            <a className="btn btn-dark btn-wide" href={tgLink(t)} target="_blank" rel="noopener">
              {t('ctaDiscuss')}
            </a>
            <a className="btn btn-outline btn-wide" href="#services">
              {t('ctaServices')}
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
```

- [ ] **Step 3: Terminal.tsx (порт анимации из index.html один в один)**

```tsx
import { useEffect, useMemo, useState } from 'react'
import { useContent } from '../content'

type Line = { type: 'cmd' | 'ok' | 'info'; text: string }

const STATUS_COST = 12
const LOOP_PAUSE = 90
const TICK_MS = 45

export function terminalLines(t: (k: string) => string): Line[] {
  return [
    { type: 'cmd', text: 'git clone your-idea && cd your-idea' },
    { type: 'ok', text: t('termScope') },
    { type: 'cmd', text: 'npm run build' },
    { type: 'ok', text: t('termStack1') },
    { type: 'ok', text: t('termStack2') },
    { type: 'ok', text: t('termTests') },
    { type: 'cmd', text: 'npm run deploy --production' },
    { type: 'info', text: t('termDeploying') },
    { type: 'ok', text: t('termLive') },
  ]
}

function totalSteps(lines: Line[]): number {
  return lines.reduce((n, l) => n + (l.type === 'cmd' ? l.text.length : STATUS_COST), 0)
}

export function Terminal() {
  const { t, lang } = useContent()
  const [step, setStep] = useState(0)
  const lines = useMemo(() => terminalLines(t), [t, lang])
  const total = useMemo(() => totalSteps(lines), [lines])

  useEffect(() => {
    const id = setInterval(
      () => setStep((s) => (s >= total + LOOP_PAUSE ? 0 : s + 1)),
      TICK_MS,
    )
    return () => clearInterval(id)
  }, [total])

  const rows: JSX.Element[] = []
  let consumed = 0
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const cost = line.type === 'cmd' ? line.text.length : STATUS_COST
    if (step <= consumed) break
    const avail = step - consumed
    const isLast = avail < cost
    if (line.type === 'cmd') {
      const txt = isLast ? line.text.slice(0, avail) : line.text
      rows.push(
        <div key={i}>
          <span className="t-prompt">$ </span>
          <span className="t-cmd">{txt}</span>
        </div>,
      )
    } else if (isLast) {
      break
    } else {
      rows.push(
        <div key={i}>
          <span className={`t-${line.type}`}>{'  ' + (line.type === 'ok' ? '✓ ' : '→ ')}</span>
          <span className="t-text">{line.text}</span>
        </div>,
      )
    }
    if (isLast) break
    consumed += cost
  }
  const blinkOn = Math.floor(step / 10) % 2 === 0

  return (
    <section className="terminal-section">
      <div className="terminal">
        <div className="terminal-bar">
          <span className="light"></span>
          <span className="light"></span>
          <span className="light light-accent"></span>
          <span className="terminal-title">{t('termTitle')}</span>
        </div>
        <div className="terminal-body" aria-hidden="true">
          {rows}
          <span className={'terminal-cursor' + (blinkOn ? '' : ' off')}></span>
        </div>
      </div>
    </section>
  )
}
```

Примечание: если `JSX.Element` не резолвится (новый JSX-рантайм), заменить тип массива на `import type { ReactElement } from 'react'` и `ReactElement[]`.

- [ ] **Step 4: ScrollSquare.tsx**

```tsx
import { useEffect, useRef } from 'react'

export function ScrollSquare() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduceMotion) return
    const onScroll = () => {
      const el = ref.current
      if (!el) return
      const doc = document.documentElement
      const max = Math.max(1, doc.scrollHeight - window.innerHeight)
      const p = Math.min(1, Math.max(0, window.scrollY / max))
      el.style.transform = `rotate(${p * 540}deg)`
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return <div ref={ref} className="scroll-square" aria-hidden="true"></div>
}
```

- [ ] **Step 5: Landing.tsx и App.tsx**

`frontend/src/sections/Landing.tsx`:

```tsx
import { Header } from './Header'
import { Hero } from './Hero'
import { ScrollSquare } from './ScrollSquare'
import { Terminal } from './Terminal'

export function Landing() {
  return (
    <div id="top">
      <ScrollSquare />
      <Header />
      <Hero />
      <Terminal />
    </div>
  )
}
```

`frontend/src/App.tsx` — полная замена:

```tsx
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ContentProvider } from './content'
import { Landing } from './sections/Landing'

export default function App() {
  return (
    <BrowserRouter>
      <ContentProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
        </Routes>
      </ContentProvider>
    </BrowserRouter>
  )
}
```

- [ ] **Step 6: Проверка типов, сборки и живого рендера**

Run: `cd frontend && npx tsc --noEmit -p tsconfig.app.json && npm run build`
Expected: без ошибок.
Затем `npm run dev` и открыть `http://localhost:5173`: шапка, hero и печатающий терминал выглядят как в `index.html` (бэкенд можно не поднимать — сработает фоллбэк).

- [ ] **Step 7: Коммит**

```bash
git add frontend/src/
git commit -m "feat(frontend): header, hero, terminal and scroll square sections"
```

---

### Task 7: Frontend — секции About, Services, Stack, Cta, Footer

**Files:**
- Create: `frontend/src/sections/About.tsx`, `frontend/src/sections/Services.tsx`, `frontend/src/sections/Stack.tsx`, `frontend/src/sections/Cta.tsx`, `frontend/src/sections/Footer.tsx`
- Modify: `frontend/src/sections/Landing.tsx`

**Interfaces:**
- Consumes: `useContent()` (Task 5), `tgLink` (Task 6).
- Produces: завершённый компонент `Landing` — полный лендинг.

- [ ] **Step 1: About.tsx**

```tsx
import { useContent } from '../content'

export function About() {
  const { t } = useContent()
  return (
    <section id="about" className="section">
      <div className="section-inner about-grid">
        <div className="about-head">
          <h2>{t('aboutTitle')}</h2>
          <div className="about-shapes" aria-hidden="true">
            <span className="shape-circle-fill"></span>
            <span className="shape-circle-line"></span>
            <span className="shape-square-fill"></span>
            <span className="shape-square-line"></span>
          </div>
        </div>
        <div className="about-text">
          <p>{t('aboutP1')}</p>
          <p>{t('aboutP2')}</p>
        </div>
      </div>
    </section>
  )
}
```

- [ ] **Step 2: Services.tsx**

```tsx
import { useContent } from '../content'

const CARDS = [
  { icon: 'icon-circle', title: 'svc1Title', text: 'svc1Text' },
  { icon: 'icon-square-line', title: 'svc2Title', text: 'svc2Text' },
  { icon: 'icon-diamond', title: 'svc3Title', text: 'svc3Text' },
  { icon: 'icon-arch', title: 'svc4Title', text: 'svc4Text' },
]

export function Services() {
  const { t } = useContent()
  return (
    <section id="services" className="section">
      <div className="section-inner">
        <h2>{t('servicesTitle')}</h2>
        <div className="services-grid">
          {CARDS.map((c) => (
            <div className="service-card" key={c.title}>
              <span className={c.icon} aria-hidden="true"></span>
              <h3>{t(c.title)}</h3>
              <p>{t(c.text)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

- [ ] **Step 3: Stack.tsx**

```tsx
import { useContent } from '../content'

const COLS = [
  { dot: 'stack-dot-accent', title: 'stackFront', items: 'stackFrontItems' },
  { dot: 'stack-dot-ink', title: 'stackBack', items: 'stackBackItems' },
  { dot: 'stack-dot-ring', title: 'stackInfra', items: 'stackInfraItems' },
]

export function Stack() {
  const { t } = useContent()
  return (
    <section id="stack" className="section">
      <div className="section-inner">
        <h2>{t('stackTitle')}</h2>
        <div className="stack-grid">
          {COLS.map((c) => (
            <div className="stack-col" key={c.title}>
              <h3>
                <span className={c.dot} aria-hidden="true"></span>
                <span>{t(c.title)}</span>
              </h3>
              <p>{t(c.items)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

- [ ] **Step 4: Cta.tsx**

```tsx
import { useContent } from '../content'
import { tgLink } from './Header'

export function Cta() {
  const { t } = useContent()
  return (
    <section className="cta-section">
      <div className="cta">
        <div className="cta-shape-ring" aria-hidden="true"></div>
        <div className="cta-shape-dot" aria-hidden="true"></div>
        <div className="cta-inner">
          <h2>{t('ctaTitle')}</h2>
          <p>{t('ctaText')}</p>
          <a className="btn btn-light btn-wide" href={tgLink(t)} target="_blank" rel="noopener">
            {t('ctaHeader')}
          </a>
        </div>
      </div>
    </section>
  )
}
```

- [ ] **Step 5: Footer.tsx**

```tsx
import { useContent } from '../content'
import { tgLink } from './Header'

export function Footer() {
  const { t } = useContent()
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <span className="logo-dot"></span>
            <span>{t('brandName')}</span>
          </div>
          <div className="footer-meta">
            <span className="footer-copy">{t('footCopyright')}</span>
            <div className="footer-social">
              <a href={tgLink(t)} target="_blank" rel="noopener">
                Telegram
              </a>
              <a href="#top">GitHub</a>
              <a href="#top">LinkedIn</a>
            </div>
          </div>
        </div>
        <div className="footer-cols">
          <div className="footer-col">
            <span className="footer-col-title">{t('servicesTitle')}</span>
            <a href="#services">{t('svc1Title')}</a>
            <a href="#services">{t('svc2Title')}</a>
            <a href="#services">{t('svc3Title')}</a>
            <a href="#services">{t('svc4Title')}</a>
          </div>
          <div className="footer-col">
            <span className="footer-col-title">{t('footCompany')}</span>
            <a href="#about">{t('aboutTitle')}</a>
            <a href="#stack">{t('stackTitle')}</a>
            <a href="#top">{t('footTop')}</a>
          </div>
          <div className="footer-col">
            <span className="footer-col-title">{t('footContact')}</span>
            <a href={tgLink(t)} target="_blank" rel="noopener">
              {t('ctaHeader')}
            </a>
            <span className="footer-note">{t('footReply')}</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
```

- [ ] **Step 6: Собрать Landing.tsx целиком**

Полная замена `frontend/src/sections/Landing.tsx`:

```tsx
import { About } from './About'
import { Cta } from './Cta'
import { Footer } from './Footer'
import { Header } from './Header'
import { Hero } from './Hero'
import { ScrollSquare } from './ScrollSquare'
import { Services } from './Services'
import { Stack } from './Stack'
import { Terminal } from './Terminal'

export function Landing() {
  return (
    <div id="top">
      <ScrollSquare />
      <Header />
      <Hero />
      <Terminal />
      <About />
      <Services />
      <Stack />
      <Cta />
      <Footer />
    </div>
  )
}
```

- [ ] **Step 7: Проверка и коммит**

Run: `cd frontend && npm test && npx tsc --noEmit -p tsconfig.app.json && npm run build`
Expected: всё PASS/успех.

```bash
git add frontend/src/
git commit -m "feat(frontend): about, services, stack, cta and footer sections"
```

---

### Task 8: Frontend — админка /admin

**Files:**
- Create: `frontend/src/admin/Admin.tsx`, `frontend/src/admin/admin.css`
- Modify: `frontend/src/App.tsx` (роут), `frontend/src/main.tsx` (импорт admin.css)

**Interfaces:**
- Consumes: `GET /api/content` (label/section в ответе), `POST /api/auth/login`, `GET /api/auth/me`, `PUT /api/content/{key}` (Task 2–4); `ContentMap`, `fetchContent` (Task 5).
- Produces: компонент `Admin` на роуте `/admin`.

- [ ] **Step 1: admin.css**

```css
.admin {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 32px 80px;
  font-family: var(--sans);
  color: var(--ink);
}
.admin h1 { font-size: 32px; margin: 0 0 32px; }
.admin h2 { font-size: 20px; margin: 40px 0 16px; }
.admin-login {
  max-width: 380px;
  margin: 120px auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.admin-login input,
.admin-row textarea {
  font: inherit;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--paper);
  color: var(--ink);
  box-sizing: border-box;
  width: 100%;
}
.admin-login button,
.admin-row button {
  font: inherit;
  cursor: pointer;
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  background: var(--ink);
  color: var(--paper);
}
.admin-row button:disabled { opacity: 0.5; cursor: default; }
.admin-row {
  display: grid;
  grid-template-columns: 220px 1fr 1fr 120px;
  gap: 12px;
  align-items: start;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}
.admin-row .admin-label { font-size: 14px; padding-top: 10px; }
.admin-row .admin-key { display: block; font-size: 12px; opacity: 0.6; }
.admin-error { color: #b3261e; font-size: 14px; }
.admin-saved { color: #2e7d32; font-size: 14px; }
@media (max-width: 800px) {
  .admin-row { grid-template-columns: 1fr; }
}
```

- [ ] **Step 2: Admin.tsx**

```tsx
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { fetchContent } from '../content'
import type { ContentMap } from '../content'

type RowState = { ru: string; en: string; status: 'idle' | 'saving' | 'saved' | 'error' }

function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    if (res.ok) onSuccess()
    else setError(res.status === 401 ? 'Неверный пароль' : 'Ошибка сервера, попробуйте ещё раз')
  }

  return (
    <form className="admin-login" onSubmit={submit}>
      <h1>Админка</h1>
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoFocus
      />
      <button type="submit">Войти</button>
      {error && <span className="admin-error">{error}</span>}
    </form>
  )
}

export function Admin() {
  const [authed, setAuthed] = useState<boolean | null>(null)
  const [texts, setTexts] = useState<ContentMap>({})
  const [rows, setRows] = useState<Record<string, RowState>>({})

  useEffect(() => {
    fetch('/api/auth/me').then((r) => setAuthed(r.ok))
  }, [])

  useEffect(() => {
    if (!authed) return
    fetchContent().then((data) => {
      setTexts(data)
      const init: Record<string, RowState> = {}
      for (const [key, v] of Object.entries(data)) {
        init[key] = { ru: v.ru, en: v.en, status: 'idle' }
      }
      setRows(init)
    })
  }, [authed])

  if (authed === null) return null
  if (!authed) return <LoginForm onSuccess={() => setAuthed(true)} />

  const setRow = (key: string, patch: Partial<RowState>) =>
    setRows((r) => ({ ...r, [key]: { ...r[key], ...patch } }))

  const save = async (key: string) => {
    setRow(key, { status: 'saving' })
    const { ru, en } = rows[key]
    const res = await fetch(`/api/content/${key}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ru, en }),
    })
    if (res.status === 401) {
      setAuthed(false)
      return
    }
    setRow(key, { status: res.ok ? 'saved' : 'error' })
  }

  const sections = new Map<string, string[]>()
  for (const [key, v] of Object.entries(texts)) {
    const s = v.section ?? ''
    if (!sections.has(s)) sections.set(s, [])
    sections.get(s)!.push(key)
  }

  return (
    <div className="admin">
      <h1>Тексты лендинга</h1>
      {[...sections.entries()].map(([section, keys]) => (
        <section key={section}>
          <h2>{section}</h2>
          {keys.map((key) => {
            const row = rows[key]
            if (!row) return null
            return (
              <div className="admin-row" key={key}>
                <div className="admin-label">
                  {texts[key].label}
                  <span className="admin-key">{key}</span>
                </div>
                <textarea
                  rows={2}
                  value={row.ru}
                  onChange={(e) => setRow(key, { ru: e.target.value, status: 'idle' })}
                />
                <textarea
                  rows={2}
                  value={row.en}
                  onChange={(e) => setRow(key, { en: e.target.value, status: 'idle' })}
                />
                <div>
                  <button onClick={() => save(key)} disabled={row.status === 'saving'}>
                    {row.status === 'saving' ? 'Сохраняю…' : 'Сохранить'}
                  </button>
                  {row.status === 'saved' && <div className="admin-saved">Сохранено</div>}
                  {row.status === 'error' && (
                    <div className="admin-error">Ошибка сохранения</div>
                  )}
                </div>
              </div>
            )
          })}
        </section>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Подключить роут и стили**

В `frontend/src/App.tsx` добавить импорт `import { Admin } from './admin/Admin'` и роут `<Route path="/admin" element={<Admin />} />` рядом с корневым. В `frontend/src/main.tsx` добавить `import './admin/admin.css'`.

- [ ] **Step 4: Ручная проверка**

Запустить бэкенд (`cd backend && ADMIN_PASSWORD=dev .venv/bin/uvicorn app.main:app --reload`) и фронт (`cd frontend && npm run dev`). Открыть `http://localhost:5173/admin`: логин с неверным паролем — «Неверный пароль»; с `dev` — таблица по секциям; правка heroTitle и «Сохранить» — «Сохранено», на `/` новый заголовок.

- [ ] **Step 5: Проверка типов и коммит**

Run: `cd frontend && npx tsc --noEmit -p tsconfig.app.json && npm run build`
Expected: успех.

```bash
git add frontend/src/
git commit -m "feat(frontend): admin page with login and per-row content editing"
```

---

### Task 9: Docker — образ, compose, раздача SPA бэкендом

**Files:**
- Create: `Dockerfile`, `docker-compose.yml`, `.dockerignore`
- Modify: `backend/app/main.py` (раздача статики), `backend/tests/test_content.py` (тест SPA-фоллбэка)

**Interfaces:**
- Consumes: `create_app` (Task 2), `frontend/dist` (Task 5–8).
- Produces: образ, где FastAPI раздаёт SPA (`/` и `/admin` → `index.html`, `/assets/*` → статика); `docker compose up` поднимает всё на `:8000` с volume `./data`.

- [ ] **Step 1: Тест на SPA-фоллбэк**

Добавить в `backend/tests/test_content.py`:

```python
def test_spa_fallback_serves_index(client, tmp_path, monkeypatch):
    import os

    static = tmp_path / "dist"
    (static / "assets").mkdir(parents=True)
    (static / "index.html").write_text("<html>SPA</html>", encoding="utf-8")
    (static / "assets" / "app.js").write_text("// js", encoding="utf-8")
    os.environ["STATIC_DIR"] = str(static)
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app()) as c:
        assert c.get("/").text == "<html>SPA</html>"
        assert c.get("/admin").text == "<html>SPA</html>"
        assert c.get("/assets/app.js").text == "// js"
        assert c.get("/api/content").status_code == 200
    del os.environ["STATIC_DIR"]
```

Run: `cd backend && .venv/bin/pytest tests/test_content.py::test_spa_fallback_serves_index -v`
Expected: FAIL (404 на `/`)

- [ ] **Step 2: Реализовать раздачу статики в main.py**

В `backend/app/main.py` добавить импорты `from fastapi.responses import FileResponse` и `from fastapi.staticfiles import StaticFiles`, а перед `return app` вставить:

```python
    static_dir = os.environ.get("STATIC_DIR", "")
    if static_dir and Path(static_dir).is_dir():
        static = Path(static_dir)
        app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            file = static / path
            if path and file.is_file():
                return FileResponse(file)
            return FileResponse(static / "index.html")
```

Run: `cd backend && .venv/bin/pytest -v` — все PASS.

- [ ] **Step 3: .dockerignore**

```
**/node_modules
**/dist
**/.venv
**/__pycache__
data
.env
.git
.playwright-mcp
docs
```

- [ ] **Step 4: Dockerfile**

```dockerfile
FROM node:22-alpine AS frontend
WORKDIR /build
COPY shared/ shared/
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci
COPY frontend/ frontend/
RUN cd frontend && npm run build

FROM python:3.12-slim
WORKDIR /srv
COPY backend/pyproject.toml backend/
COPY backend/app backend/app
COPY shared/ shared/
RUN pip install --no-cache-dir ./backend
COPY --from=frontend /build/frontend/dist frontend/dist
ENV DB_PATH=/srv/data/content.db \
    SEED_PATH=/srv/shared/seed_content.json \
    STATIC_DIR=/srv/frontend/dist
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
```

- [ ] **Step 5: docker-compose.yml**

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data:/srv/data
    restart: unless-stopped
```

- [ ] **Step 6: Проверить сборку и запуск**

```bash
cp .env.example .env
docker compose up -d --build
curl -s http://localhost:8000/api/content | head -c 200   # JSON с текстами
curl -s http://localhost:8000/ | head -c 100              # HTML SPA
docker compose down
```

Expected: оба curl возвращают ожидаемое содержимое.

- [ ] **Step 7: Коммит**

```bash
git add Dockerfile docker-compose.yml .dockerignore backend/
git commit -m "feat(infra): multi-stage Docker image, compose, SPA serving from FastAPI"
```

---

### Task 10: CI/CD — GitHub Actions

**Files:**
- Create: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`

**Interfaces:**
- Consumes: тесты и сборки из Task 2–9.
- Produces: CI на каждый push/PR; деплой-воркфлоу по успеху CI в main, пропускается без секретов `VPS_HOST`/`VPS_USER`/`VPS_SSH_KEY`.

- [ ] **Step 1: ci.yml**

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      # -e обязателен: обычная установка уводит app/__file__ в site-packages,
      # и дефолтный SEED_PATH (backend/../shared) перестаёт существовать
      - run: pip install -e "./backend[dev]"
      - run: ruff check backend
      - run: pytest backend/tests -v

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npx tsc --noEmit -p tsconfig.app.json
      - run: npm test
      - run: npm run build

  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t prodev-landing .
```

- [ ] **Step 2: deploy.yml**

```yaml
name: Deploy

on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.event.workflow_run.conclusion == 'success'
    steps:
      - name: Проверить секреты VPS
        id: check
        env:
          VPS_HOST: ${{ secrets.VPS_HOST }}
        run: |
          if [ -n "$VPS_HOST" ]; then
            echo "ok=true" >> "$GITHUB_OUTPUT"
          else
            echo "Секреты VPS не заданы — деплой пропущен."
          fi
      - name: Деплой по SSH
        if: steps.check.outputs.ok == 'true'
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/prodev-landing
            git pull --ff-only
            docker compose up -d --build
```

- [ ] **Step 3: Проверить синтаксис локально и запушить**

```bash
python3 -c "import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]; print('ok')"
git add .github/
git commit -m "ci: lint+test+build workflows and guarded VPS deploy"
git push origin main
```

Затем: `gh run watch --exit-status` (или `gh run list --limit 3`) — CI должен пройти зелёным. Deploy-воркфлоу должен завершиться со «секреты не заданы — пропущен».

---

### Task 11: Визуальный паритет и удаление legacy index.html

**Files:**
- Delete: `index.html` (корень)
- Modify: `README.md` (финальная версия из Task 1 — актуализировать при расхождениях)

- [ ] **Step 1: Поднять прод-сборку и снять скриншоты**

```bash
docker compose up -d --build
```

Через Playwright MCP: открыть `http://localhost:8000/`, viewport 1280×900, full-page скриншот; переключить EN, скриншот; viewport 390×844, скриншот. Затем открыть эталон (`python3 -m http.server 8900` в корне → `http://localhost:8900/index.html`) и снять те же скриншоты.

- [ ] **Step 2: Сравнить глазами**

Критерий: совпадение секций, цветов, шрифтов, радиусов, отступов, анимаций (терминал печатает, квадратик крутится). Любое расхождение — исправить в соответствующей секции фронта и повторить.

- [ ] **Step 3: Проверить админку на прод-сборке**

`http://localhost:8000/admin` → логин (пароль из `.env`) → правка любого текста → текст меняется на `http://localhost:8000/` после перезагрузки страницы.

- [ ] **Step 4: Удалить эталон и закоммитить**

```bash
git rm index.html
git add README.md
git commit -m "chore: remove legacy static landing after SPA parity check"
git push origin main
docker compose down
```

Expected: CI зелёный. Проект завершён.

---

## Итоговая проверка соответствия спеке

- Тексты в SQLite, сид из `shared/seed_content.json` — Task 1, 2.
- `GET /api/content` `{key:{ru,en,label,section}}` — Task 2 (label/section включены: нужны админке, публичность безвредна — осознанное уточнение спеки).
- Логин/логаут/сессия + `GET /api/auth/me` для восстановления сессии в админке — Task 3.
- `PUT /api/content/{key}` (401/404) — Task 4.
- SPA React+Vite+TS, перенос вёрстки, фоллбэк, `prodev_lang` — Task 5–7.
- Админка `/admin` — Task 8.
- Docker single-container + volume + compose — Task 9.
- CI + guarded deploy — Task 10.
- Паритет и удаление `index.html` — Task 11.
- Публичная репа `alexpuzhdev/prodev-landing` — Task 1.
