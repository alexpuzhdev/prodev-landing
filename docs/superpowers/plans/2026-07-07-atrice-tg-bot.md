# atrice Telegram-бот Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Меню-бот студии (портфолио, услуги, анкета заявки, о студии) отдельным aiogram-сервисом; заявки в личку владельцу и в базу; управление контентом и заявками из существующей админки.

**Architecture:** Бот (aiogram 3, long polling) в отдельном compose-сервисе, ходит в бэкенд по внутренней сети: контент через публичные GET, заявки через POST /api/leads с сервисным токеном. Бэкенд остаётся единственным писателем SQLite. Картинки портфолио: загрузка в админке, файлы в data/uploads, бот скачивает байты у бэкенда и отправляет в Telegram файлом.

**Tech Stack:** aiogram >= 3.13, httpx; FastAPI + SQLAlchemy (существующие); python-multipart для загрузки файлов; React-админка.

**Спека:** `docs/superpowers/specs/2026-07-07-atrice-tg-bot-design.md`.

## Global Constraints

- Правила репо: `CLAUDE.md` (AI-маркеры запрещены, коммиты одной строкой `<type>(<scope>): ...` без плашек, НОВЫЕ ТЕСТЫ НЕ ПИСАТЬ, существующие pytest гонять перед коммитом).
- Секреты (BOT_TOKEN, SERVICE_TOKEN, OWNER_CHAT_ID) только в .env, в git не попадают.
- Бот одноязычный (русский); ключи контента дублируют ru в en.
- Python-код совместим с 3.10 локально, 3.12 в Docker; ruff line-length 100.
- pip локально: индекс `https://nexus-omg.pak-cspmz.ru/repository/iro-pypi-group/simple/` c `--cert /home/PAK-CSPMZ/apuzhinskii/work_dir/certs/certs/omg-nexus.crt`.
- Проверки перед каждым коммитом: `backend/.venv/bin/pytest -q` (7 passed), `ruff check`, для фронта `npx tsc --noEmit -p tsconfig.app.json && npm run build`.
- Пуш в main = автодеплой: пушить только в конце, когда всё проверено локально.

---

### Task 1: Backend - заявки (leads)

**Files:**
- Create: `backend/app/leads.py`
- Modify: `backend/app/models.py`, `backend/app/main.py`, `backend/app/access.py`, `.env.example`

**Interfaces:**
- Produces: модель `Lead`; `POST /api/leads` (заголовок `X-Service-Token`) body `{tg_user_id:int, username:str, name:str, task:str, project_type:str, timeline:str}` -> 200 `{id}` | 401; `GET /api/leads` (админ) -> список новых сверху; `PATCH /api/leads/{id}` body `{status: "new"|"done"}` -> 200 | 404; `app.state.service_token`.

- [ ] **Step 1: Модель Lead в models.py** (после TerminalLine)

```python
class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(default=0)
    username: Mapped[str] = mapped_column(default="")
    name: Mapped[str] = mapped_column(default="")
    task: Mapped[str] = mapped_column(default="")
    project_type: Mapped[str] = mapped_column(default="")
    timeline: Mapped[str] = mapped_column(default="")
    status: Mapped[str] = mapped_column(default="new")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
```

- [ ] **Step 2: Роутер backend/app/leads.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import require_admin
from .db import get_db
from .models import Lead

router = APIRouter(prefix="/api/leads")

STATUSES = ("new", "done")


class LeadCreate(BaseModel):
    tg_user_id: int
    username: str = ""
    name: str = ""
    task: str
    project_type: str
    timeline: str


class LeadPatch(BaseModel):
    status: str


def require_service_token(request: Request) -> None:
    expected = request.app.state.service_token
    if not expected or request.headers.get("x-service-token") != expected:
        raise HTTPException(status_code=401, detail="Неверный сервисный токен")


def _serialize(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "tg_user_id": lead.tg_user_id,
        "username": lead.username,
        "name": lead.name,
        "task": lead.task,
        "project_type": lead.project_type,
        "timeline": lead.timeline,
        "status": lead.status,
        "created_at": lead.created_at.isoformat(),
    }


@router.post("", dependencies=[Depends(require_service_token)])
def create_lead(body: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        tg_user_id=body.tg_user_id,
        username=body.username,
        name=body.name,
        task=body.task,
        project_type=body.project_type,
        timeline=body.timeline,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"id": lead.id}


@router.get("", dependencies=[Depends(require_admin)])
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc(), Lead.id.desc()).all()
    return [_serialize(lead) for lead in leads]


@router.patch("/{lead_id}", dependencies=[Depends(require_admin)])
def patch_lead(lead_id: int, body: LeadPatch, db: Session = Depends(get_db)):
    if body.status not in STATUSES:
        raise HTTPException(status_code=422, detail="status: new или done")
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    lead.status = body.status
    db.commit()
    return _serialize(lead)
```

- [ ] **Step 3: main.py** - импорт `from . import auth, content, leads, terminal`, после существующих include: `app.include_router(leads.router)`; рядом с admin_password: `app.state.service_token = os.environ.get("SERVICE_TOKEN", "")`.

- [ ] **Step 4: access.py** - POST /api/leads идёт от бота из docker-сети и НЕ должен резаться IP-гейтом (авторизация сервисным токеном), а GET /api/leads админский. Заменить функцию `is_admin_request`:

```python
def is_admin_request(request: Request) -> bool:
    path = request.url.path
    method = request.method
    if path == "/api/leads" and method == "POST":
        return False
    if path == "/admin" or path.startswith("/admin/"):
        return True
    if path.startswith("/api/auth") or path.startswith("/api/leads"):
        return True
    return path.startswith("/api/") and method not in SAFE_METHODS
```

- [ ] **Step 5: .env.example** - добавить блок:

```bash
# Telegram-бот
BOT_TOKEN=
# chat id владельца: бот шлёт туда заявки
OWNER_CHAT_ID=
# общий секрет бота и бэкенда для POST /api/leads (openssl rand -hex 32)
SERVICE_TOKEN=
```

- [ ] **Step 6: Проверка живьём** (uvicorn с env SERVICE_TOKEN=t1, ADMIN_PASSWORD=dev, DB в scratchpad):

```bash
curl -s -X POST localhost:8000/api/leads -H 'Content-Type: application/json' -d '{"tg_user_id":1,"task":"x","project_type":"mvp","timeline":"y"}'                    # 401
curl -s -X POST localhost:8000/api/leads -H 'X-Service-Token: t1' -H 'Content-Type: application/json' -d '{"tg_user_id":1,"username":"u","name":"n","task":"x","project_type":"mvp","timeline":"y"}'   # {"id":1}
curl -s localhost:8000/api/leads                                                     # 401 (нет сессии)
# login и GET с cookie -> список с одной заявкой; PATCH status=done -> status меняется
```

- [ ] **Step 7: pytest + ruff + коммит**

```bash
cd backend && .venv/bin/pytest -q && .venv/bin/ruff check .
git add backend/ .env.example && git commit -m "feat(backend): leads api with service token and admin listing"
```

---

### Task 2: Backend - портфолио и загрузка картинок

**Files:**
- Create: `backend/app/portfolio.py`
- Modify: `backend/app/models.py`, `backend/app/main.py`, `backend/pyproject.toml` (python-multipart), `Dockerfile` (mkdir uploads не нужен: создаётся кодом)

**Interfaces:**
- Produces: модель `PortfolioItem`; `GET /api/portfolio` (публичный, только enabled, сортировка по position; `?all=1` с админ-сессией отдаёт все) -> `[{id, position, title, text, image_path, enabled}]`, image_path вида `/uploads/<file>`; `POST /api/portfolio` (админ, multipart: title, text, position, image-файл) -> объект; `PUT /api/portfolio/{id}` (админ, multipart, image опциональна); `DELETE /api/portfolio/{id}` (админ); статика `/uploads/*`.

- [ ] **Step 1: Модель PortfolioItem в models.py**

```python
class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(default=0)
    title: Mapped[str] = mapped_column(default="")
    text: Mapped[str] = mapped_column(default="")
    image_path: Mapped[str] = mapped_column(default="")
    enabled: Mapped[bool] = mapped_column(default=True)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)
```

- [ ] **Step 2: зависимость** - в `backend/pyproject.toml` dependencies добавить `"python-multipart>=0.0.9",`; переустановить: `cd backend && .venv/bin/pip install --index-url https://nexus-omg.pak-cspmz.ru/repository/iro-pypi-group/simple/ --cert /home/PAK-CSPMZ/apuzhinskii/work_dir/certs/certs/omg-nexus.crt -e ".[dev]"`.

- [ ] **Step 3: Роутер backend/app/portfolio.py**

```python
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from .auth import require_admin
from .db import get_db
from .models import PortfolioItem, utcnow

router = APIRouter(prefix="/api/portfolio")

ALLOWED_EXT = (".png", ".jpg", ".jpeg", ".webp")
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def uploads_dir(request: Request) -> Path:
    return request.app.state.uploads_dir


def _serialize(item: PortfolioItem) -> dict:
    return {
        "id": item.id,
        "position": item.position,
        "title": item.title,
        "text": item.text,
        "image_path": item.image_path,
        "enabled": item.enabled,
    }


async def _save_image(request: Request, image: UploadFile) -> str:
    ext = Path(image.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=422, detail="Картинка: png, jpg или webp")
    data = await image.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=422, detail="Картинка больше 5 МБ")
    name = f"{uuid.uuid4().hex}{ext}"
    (uploads_dir(request) / name).write_bytes(data)
    return f"/uploads/{name}"


def _delete_image(request: Request, image_path: str) -> None:
    name = Path(image_path).name
    file = uploads_dir(request) / name
    if name and file.is_file():
        file.unlink()


@router.get("")
def list_items(request: Request, all: int = 0, db: Session = Depends(get_db)):
    query = db.query(PortfolioItem)
    if all:
        require_admin(request)
    else:
        query = query.filter(PortfolioItem.enabled == True)  # noqa: E712
    items = query.order_by(PortfolioItem.position, PortfolioItem.id).all()
    return [_serialize(item) for item in items]


@router.post("", dependencies=[Depends(require_admin)])
async def create_item(
    request: Request,
    image: UploadFile,
    title: str = Form(""),
    text: str = Form(""),
    position: int = Form(0),
    db: Session = Depends(get_db),
):
    image_path = await _save_image(request, image)
    item = PortfolioItem(title=title, text=text, position=position, image_path=image_path)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.put("/{item_id}", dependencies=[Depends(require_admin)])
async def update_item(
    request: Request,
    item_id: int,
    image: UploadFile | None = None,
    title: str = Form(""),
    text: str = Form(""),
    position: int = Form(0),
    enabled: int = Form(1),
    db: Session = Depends(get_db),
):
    item = db.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Карточка не найдена")
    if image is not None and image.filename:
        _delete_image(request, item.image_path)
        item.image_path = await _save_image(request, image)
    item.title = title
    item.text = text
    item.position = position
    item.enabled = bool(enabled)
    item.updated_at = utcnow()
    db.commit()
    return _serialize(item)


@router.delete("/{item_id}", dependencies=[Depends(require_admin)])
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Карточка не найдена")
    _delete_image(request, item.image_path)
    db.delete(item)
    db.commit()
    return {"ok": True}
```

- [ ] **Step 4: main.py** - импорт portfolio, `app.include_router(portfolio.router)`; после вычисления db_path:

```python
    uploads_path = Path(os.environ.get("UPLOADS_DIR", db_path.parent / "uploads"))
    uploads_path.mkdir(parents=True, exist_ok=True)
    app.state.uploads_dir = uploads_path
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
```

Внимание: mount `/uploads` должен идти ДО catch-all `/{path:path}` (SPA), то есть в блоке до условия static_dir. Fastapi матчит mounts до роутов, но регистрировать до catch-all надёжнее.

- [ ] **Step 5: Проверка живьём** - login-cookie, затем:

```bash
printf 'x' > /tmp/t.png не годится: сделать настоящий png через python (PIL нет, взять frontend/public/og.png)
curl -s -b cookies -X POST localhost:8000/api/portfolio -F title=Кейс -F text=Описание -F position=10 -F image=@frontend/public/og.png    # объект с /uploads/<hex>.png
curl -s localhost:8000/api/portfolio                        # массив с карточкой
curl -s -o /dev/null -w '%{http_code}' localhost:8000/uploads/<hex>.png   # 200
DELETE -> файл исчез из data-каталога
```

- [ ] **Step 6: pytest + ruff + коммит** `feat(backend): portfolio crud with image uploads`

---

### Task 3: Контент бота - сид и миграция 007

**Files:**
- Modify: `shared/seed_content.json`, `backend/app/migrations.py`

**Interfaces:**
- Produces: ключи секции "Бот" в content (botWelcome, botMenuPortfolio, botMenuServices, botMenuLead, botMenuAbout, botBack, botPortfolioEmpty, botAboutSite, botLeadAskTask, botLeadAskType, botLeadTypeMvp, botLeadTypeLanding, botLeadTypeWebapp, botLeadTypeSupport, botLeadAskTimeline, botLeadConfirm, botLeadSend, botLeadCancel, botLeadThanks, botLeadCancelled, botError). Бот читает их из GET /api/content.

- [ ] **Step 1: Добавить в seed_content.json перед "telegramHandle"** (en == ru у всех):

```json
  "botWelcome":        {"ru": "Привет! Это бот студии atrice. Выберите раздел:", "en": "Привет! Это бот студии atrice. Выберите раздел:", "label": "Приветствие /start", "section": "Бот"},
  "botMenuPortfolio":  {"ru": "Портфолио", "en": "Портфолио", "label": "Кнопка меню: портфолио", "section": "Бот"},
  "botMenuServices":   {"ru": "Услуги", "en": "Услуги", "label": "Кнопка меню: услуги", "section": "Бот"},
  "botMenuLead":       {"ru": "Оставить заявку", "en": "Оставить заявку", "label": "Кнопка меню: заявка", "section": "Бот"},
  "botMenuAbout":      {"ru": "О студии", "en": "О студии", "label": "Кнопка меню: о студии", "section": "Бот"},
  "botBack":           {"ru": "В меню", "en": "В меню", "label": "Кнопка: назад в меню", "section": "Бот"},
  "botPortfolioEmpty": {"ru": "Мы как раз оформляем портфолио. Оставьте заявку, покажем кейсы лично.", "en": "Мы как раз оформляем портфолио. Оставьте заявку, покажем кейсы лично.", "label": "Портфолио пусто", "section": "Бот"},
  "botAboutSite":      {"ru": "Открыть atrice.ru", "en": "Открыть atrice.ru", "label": "Кнопка: сайт", "section": "Бот"},
  "botLeadAskTask":    {"ru": "Расскажите в двух словах, что за задача?", "en": "Расскажите в двух словах, что за задача?", "label": "Анкета: вопрос о задаче", "section": "Бот"},
  "botLeadAskType":    {"ru": "Какой тип проекта ближе всего?", "en": "Какой тип проекта ближе всего?", "label": "Анкета: вопрос о типе", "section": "Бот"},
  "botLeadTypeMvp":    {"ru": "MVP", "en": "MVP", "label": "Анкета: тип MVP", "section": "Бот"},
  "botLeadTypeLanding": {"ru": "Лендинг", "en": "Лендинг", "label": "Анкета: тип лендинг", "section": "Бот"},
  "botLeadTypeWebapp": {"ru": "Веб-приложение", "en": "Веб-приложение", "label": "Анкета: тип веб-приложение", "section": "Бот"},
  "botLeadTypeSupport": {"ru": "Поддержка проекта", "en": "Поддержка проекта", "label": "Анкета: тип поддержка", "section": "Бот"},
  "botLeadAskTimeline": {"ru": "Какие сроки хотите? Например: месяц, к марту, не горит.", "en": "Какие сроки хотите? Например: месяц, к марту, не горит.", "label": "Анкета: вопрос о сроках", "section": "Бот"},
  "botLeadConfirm":    {"ru": "Проверьте заявку:", "en": "Проверьте заявку:", "label": "Анкета: подтверждение", "section": "Бот"},
  "botLeadSend":       {"ru": "Отправить", "en": "Отправить", "label": "Анкета: кнопка отправить", "section": "Бот"},
  "botLeadCancel":     {"ru": "Отмена", "en": "Отмена", "label": "Анкета: кнопка отмена", "section": "Бот"},
  "botLeadThanks":     {"ru": "Спасибо! Заявка у нас, ответим в течение дня.", "en": "Спасибо! Заявка у нас, ответим в течение дня.", "label": "Анкета: благодарность", "section": "Бот"},
  "botLeadCancelled":  {"ru": "Заявка отменена. Возвращаю в меню.", "en": "Заявка отменена. Возвращаю в меню.", "label": "Анкета: отменено", "section": "Бот"},
  "botError":          {"ru": "Сервис временно недоступен, попробуйте позже.", "en": "Сервис временно недоступен, попробуйте позже.", "label": "Ошибка сервиса", "section": "Бот"},
```

- [ ] **Step 2: Миграция 007** - вставляет эти же ключи в существующие базы, если ключа ещё нет. В migrations.py:

```python
def _007_bot_content(session: Session) -> None:
    """Добавляет тексты Telegram-бота в существующие базы."""
    import json
    from pathlib import Path
    ...
```

НЕ так: импорты только на уровне модуля (правило репо). Правильно: миграция читает те же данные, что и сид. Реализация: в seed.py выделить `load_seed(seed_path) -> dict` (json.loads как сейчас), а в migrations.py:

```python
def _007_bot_content(session: Session) -> None:
    """Добавляет тексты Telegram-бота в существующие базы."""
    seed_path = Path(os.environ.get("SEED_PATH", BACKEND_DIR.parent / "shared" / "seed_content.json"))
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    for key, row in data.items():
        if row.get("section") != "Бот" or session.get(Content, key) is not None:
            continue
        session.add(
            Content(key=key, ru=row["ru"], en=row["en"], label=row.get("label", key), section="Бот")
        )
```

с модульными импортами `import json`, `import os`, `from pathlib import Path` и константой `BACKEND_DIR = Path(__file__).resolve().parent.parent` в начале migrations.py. Зарегистрировать `("007_bot_content", _007_bot_content)`.

- [ ] **Step 3: Проверка** - одноразовый скрипт: база с контентом без ключей бота -> run_migrations добавляет 21 ключ; повторный запуск ничего не делает; свежая база: сид уже содержит ключи, 007 пропускает (все есть).

- [ ] **Step 4: pytest + ruff + коммит** `feat(content): telegram bot texts in seed and migration`

---

### Task 4: Админка - вкладки, заявки, портфолио

**Files:**
- Create: `frontend/src/admin/Leads.tsx`, `frontend/src/admin/Portfolio.tsx`
- Modify: `frontend/src/admin/Admin.tsx` (вкладки), `frontend/src/admin/admin.css`

**Interfaces:**
- Consumes: `GET/PATCH /api/leads`, `GET /api/portfolio?all=1`, `POST/PUT/DELETE /api/portfolio` (Task 1-2).
- Produces: вкладки "Тексты" (текущий контент + терминал), "Заявки", "Портфолио" внутри Admin.

- [ ] **Step 1: Admin.tsx** - состояние `tab: 'texts' | 'leads' | 'portfolio'`, панель кнопок-вкладок после `<h1>`, текущее содержимое (секции текстов + терминал) рендерится при tab === 'texts', `<Leads onAuthLost={() => setAuthed(false)} />` и `<Portfolio onAuthLost={...} />` для остальных.

```tsx
const [tab, setTab] = useState<'texts' | 'leads' | 'portfolio'>('texts')
...
<div className="admin-tabs">
  <button className={tab === 'texts' ? 'active' : ''} onClick={() => setTab('texts')}>Тексты</button>
  <button className={tab === 'leads' ? 'active' : ''} onClick={() => setTab('leads')}>Заявки</button>
  <button className={tab === 'portfolio' ? 'active' : ''} onClick={() => setTab('portfolio')}>Портфолио</button>
</div>
```

- [ ] **Step 2: Leads.tsx**

```tsx
import { useEffect, useState } from 'react'

type Lead = {
  id: number
  username: string
  name: string
  task: string
  project_type: string
  timeline: string
  status: 'new' | 'done'
  created_at: string
}

const TYPE_LABELS: Record<string, string> = {
  mvp: 'MVP',
  landing: 'Лендинг',
  webapp: 'Веб-приложение',
  support: 'Поддержка',
}

export function Leads({ onAuthLost }: { onAuthLost: () => void }) {
  const [leads, setLeads] = useState<Lead[]>([])
  const [error, setError] = useState('')

  const load = async () => {
    const res = await fetch('/api/leads')
    if (res.status === 401) return onAuthLost()
    if (res.ok) setLeads(await res.json())
    else setError('Не удалось загрузить заявки')
  }

  useEffect(() => {
    load()
  }, [])

  const toggle = async (lead: Lead) => {
    const res = await fetch(`/api/leads/${lead.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: lead.status === 'new' ? 'done' : 'new' }),
    })
    if (res.status === 401) return onAuthLost()
    if (res.ok) load()
  }

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {leads.length === 0 && !error && <p className="admin-hint">Заявок пока нет.</p>}
      {leads.map((lead) => (
        <div className={'admin-lead' + (lead.status === 'done' ? ' done' : '')} key={lead.id}>
          <div className="admin-lead-head">
            <b>{lead.name || 'Без имени'}</b>
            {lead.username && (
              <a href={`https://t.me/${lead.username}`} target="_blank" rel="noopener">
                @{lead.username}
              </a>
            )}
            <span>{TYPE_LABELS[lead.project_type] ?? lead.project_type}</span>
            <span>{new Date(lead.created_at).toLocaleString('ru-RU')}</span>
            <button onClick={() => toggle(lead)}>
              {lead.status === 'new' ? 'Обработана' : 'Вернуть в новые'}
            </button>
          </div>
          <p>{lead.task}</p>
          <p className="admin-hint">Сроки: {lead.timeline}</p>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Portfolio.tsx** - список карточек (превью img, title, text, position, enabled чекбокс, Сохранить/Удалить) + форма добавления (title, text, position, file input). Все запросы FormData:

```tsx
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

type Item = {
  id: number
  position: number
  title: string
  text: string
  image_path: string
  enabled: boolean
}

export function Portfolio({ onAuthLost }: { onAuthLost: () => void }) {
  const [items, setItems] = useState<Item[]>([])
  const [error, setError] = useState('')

  const load = async () => {
    const res = await fetch('/api/portfolio?all=1')
    if (res.status === 401) return onAuthLost()
    if (res.ok) setItems(await res.json())
  }

  useEffect(() => {
    load()
  }, [])

  const save = async (item: Item, file: File | null) => {
    const fd = new FormData()
    fd.set('title', item.title)
    fd.set('text', item.text)
    fd.set('position', String(item.position))
    fd.set('enabled', item.enabled ? '1' : '0')
    if (file) fd.set('image', file)
    const res = await fetch(`/api/portfolio/${item.id}`, { method: 'PUT', body: fd })
    if (res.status === 401) return onAuthLost()
    if (res.ok) load()
    else setError('Не удалось сохранить карточку')
  }

  const remove = async (id: number) => {
    const res = await fetch(`/api/portfolio/${id}`, { method: 'DELETE' })
    if (res.status === 401) return onAuthLost()
    if (res.ok) load()
  }

  const add = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const res = await fetch('/api/portfolio', { method: 'POST', body: fd })
    if (res.status === 401) return onAuthLost()
    if (res.ok) {
      e.currentTarget.reset()
      load()
    } else {
      setError('Не удалось добавить карточку')
    }
  }
  const patch = (id: number, p: Partial<Item>) =>
    setItems((list) => list.map((it) => (it.id === id ? { ...it, ...p } : it)))

  return (
    <div>
      {error && <div className="admin-error">{error}</div>}
      {items.map((item) => (
        <div className="admin-card" key={item.id}>
          <img src={item.image_path} alt="" />
          <div className="admin-card-fields">
            <input
              value={item.title}
              placeholder="Заголовок"
              onChange={(e) => patch(item.id, { title: e.target.value })}
            />
            <textarea
              rows={3}
              value={item.text}
              placeholder="Описание"
              onChange={(e) => patch(item.id, { text: e.target.value })}
            />
            <label>
              Порядок:
              <input
                type="number"
                value={item.position}
                onChange={(e) => patch(item.id, { position: Number(e.target.value) })}
              />
            </label>
            <label>
              <input
                type="checkbox"
                checked={item.enabled}
                onChange={(e) => patch(item.id, { enabled: e.target.checked })}
              />
              Показывать в боте
            </label>
            <label>
              Заменить картинку:
              <input type="file" accept=".png,.jpg,.jpeg,.webp" id={`file-${item.id}`} />
            </label>
            <div className="admin-term-actions">
              <button
                onClick={() => {
                  const el = document.getElementById(`file-${item.id}`) as HTMLInputElement
                  save(item, el?.files?.[0] ?? null)
                }}
              >
                Сохранить
              </button>
              <button className="admin-danger" onClick={() => remove(item.id)}>
                Удалить
              </button>
            </div>
          </div>
        </div>
      ))}

      <h2>Новая карточка</h2>
      <form className="admin-card-form" onSubmit={add}>
        <input name="title" placeholder="Заголовок" />
        <textarea name="text" rows={3} placeholder="Описание" />
        <input name="position" type="number" defaultValue={10} />
        <input name="image" type="file" accept=".png,.jpg,.jpeg,.webp" required />
        <button type="submit">Добавить карточку</button>
      </form>
    </div>
  )
}
```

Полный рендер: каждая карточка в .admin-card: `<img src={item.image_path} />`, инпуты title/position, textarea text, чекбокс enabled, file input для замены, кнопки. Форма добавления: обязательный file input name="image", инпуты name="title", name="position", textarea name="text", кнопка "Добавить карточку".

- [ ] **Step 4: admin.css** - стили вкладок, .admin-lead, .admin-card (превью 120px), в духе существующих.

- [ ] **Step 5: Проверка playwright** - логин, вкладка Портфолио: добавить карточку с og.png, увидеть превью; вкладка Заявки: заявка из Task 1 видна, тумблер статуса работает; вкладка Тексты: секция "Бот" на месте.

- [ ] **Step 6: tsc + build + коммит** `feat(frontend): admin tabs for leads and portfolio`

---

### Task 5: Сервис бота (aiogram)

**Files:**
- Create: `bot/pyproject.toml`, `bot/Dockerfile`, `bot/app/__init__.py`, `bot/app/config.py`, `bot/app/backend.py`, `bot/app/keyboards.py`, `bot/app/menu.py`, `bot/app/portfolio.py`, `bot/app/lead.py`, `bot/app/main.py`
- Modify: `docker-compose.yml`, `.github/workflows/ci.yml`, `.gitignore` (ничего нового не нужно: .venv покрыт)

**Interfaces:**
- Consumes: GET /api/content, GET /api/portfolio, GET /uploads/*, POST /api/leads (Task 1-3).
- Produces: работающий бот: /start -> меню; разделы; анкета; отправка владельцу.

- [ ] **Step 1: bot/pyproject.toml**

```toml
[project]
name = "atrice-bot"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "aiogram>=3.13",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["ruff>=0.6"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["app"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: config.py**

```python
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_CHAT_ID = int(os.environ.get("OWNER_CHAT_ID", "0") or "0")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://app:8000").rstrip("/")
SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN", "")
SITE_URL = os.environ.get("SITE_URL", "https://atrice.ru")
CACHE_TTL = 120
```

- [ ] **Step 3: backend.py** - httpx.AsyncClient, кэш словарём {key: (expires, value)}:

```python
import time

import httpx

from . import config


class Backend:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=config.BACKEND_URL, timeout=10)
        self._cache: dict[str, tuple[float, object]] = {}

    async def _cached_get(self, path: str):
        now = time.monotonic()
        hit = self._cache.get(path)
        if hit and hit[0] > now:
            return hit[1]
        resp = await self._client.get(path)
        resp.raise_for_status()
        data = resp.json()
        self._cache[path] = (now + config.CACHE_TTL, data)
        return data

    async def texts(self) -> dict:
        return await self._cached_get("/api/content")

    async def text(self, key: str) -> str:
        data = await self.texts()
        row = data.get(key) or {}
        return row.get("ru") or key

    async def portfolio(self) -> list:
        return await self._cached_get("/api/portfolio")

    async def image(self, image_path: str) -> bytes:
        resp = await self._client.get(image_path)
        resp.raise_for_status()
        return resp.content

    async def create_lead(self, payload: dict) -> bool:
        resp = await self._client.post(
            "/api/leads", json=payload, headers={"X-Service-Token": config.SERVICE_TOKEN}
        )
        return resp.status_code == 200


backend = Backend()
```

- [ ] **Step 4: keyboards.py**

```python
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import config


def main_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botMenuPortfolio"], callback_data="menu:portfolio")],
            [InlineKeyboardButton(text=t["botMenuServices"], callback_data="menu:services")],
            [InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead")],
            [InlineKeyboardButton(text=t["botMenuAbout"], callback_data="menu:about")],
        ]
    )


def back_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")]]
    )


def about_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botAboutSite"], url=config.SITE_URL)],
            [InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")],
        ]
    )


def portfolio_nav(t: dict[str, str], idx: int, total: int) -> InlineKeyboardMarkup:
    nav = []
    if idx > 0:
        nav.append(InlineKeyboardButton(text="<", callback_data=f"portfolio:{idx - 1}"))
    nav.append(InlineKeyboardButton(text=f"{idx + 1}/{total}", callback_data="noop"))
    if idx < total - 1:
        nav.append(InlineKeyboardButton(text=">", callback_data=f"portfolio:{idx + 1}"))
    return InlineKeyboardMarkup(
        inline_keyboard=[nav, [InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")]]
    )


def lead_types(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botLeadTypeMvp"], callback_data="lead_type:mvp")],
            [InlineKeyboardButton(text=t["botLeadTypeLanding"], callback_data="lead_type:landing")],
            [InlineKeyboardButton(text=t["botLeadTypeWebapp"], callback_data="lead_type:webapp")],
            [InlineKeyboardButton(text=t["botLeadTypeSupport"], callback_data="lead_type:support")],
        ]
    )


def lead_confirm(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t["botLeadSend"], callback_data="lead:send"),
                InlineKeyboardButton(text=t["botLeadCancel"], callback_data="lead:cancel"),
            ]
        ]
    )
```

- [ ] **Step 5: menu.py** - роутер: /start и menu:* колбэки. Хелпер `texts()` собирает словарь нужных ключей с fallback на botError при HTTP-ошибке.

```python
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from . import keyboards
from .backend import backend

router = Router()
log = logging.getLogger(__name__)

KEYS = [
    "botWelcome", "botMenuPortfolio", "botMenuServices", "botMenuLead", "botMenuAbout",
    "botBack", "botPortfolioEmpty", "botAboutSite", "botLeadAskTask", "botLeadAskType",
    "botLeadTypeMvp", "botLeadTypeLanding", "botLeadTypeWebapp", "botLeadTypeSupport",
    "botLeadAskTimeline", "botLeadConfirm", "botLeadSend", "botLeadCancel",
    "botLeadThanks", "botLeadCancelled", "botError",
    "svc1Title", "svc1Text", "svc2Title", "svc2Text",
    "svc3Title", "svc3Text", "svc4Title", "svc4Text",
    "aboutTitle", "aboutP1", "aboutP2",
]

FALLBACK_ERROR = "Сервис временно недоступен, попробуйте позже."


async def texts() -> dict[str, str]:
    result = {}
    for key in KEYS:
        result[key] = await backend.text(key)
    return result


@router.message(CommandStart())
async def start(message: Message) -> None:
    try:
        t = await texts()
    except Exception:
        log.exception("backend unavailable")
        await message.answer(FALLBACK_ERROR)
        return
    await message.answer(t["botWelcome"], reply_markup=keyboards.main_menu(t))


@router.callback_query(F.data == "menu:main")
async def to_main(callback: CallbackQuery) -> None:
    t = await texts()
    await callback.message.answer(t["botWelcome"], reply_markup=keyboards.main_menu(t))
    await callback.answer()


@router.callback_query(F.data == "menu:services")
async def services(callback: CallbackQuery) -> None:
    t = await texts()
    lines = []
    for i in (1, 2, 3, 4):
        lines.append(f"<b>{t[f'svc{i}Title']}</b>\n{t[f'svc{i}Text']}")
    await callback.message.answer("\n\n".join(lines), reply_markup=keyboards.back_menu(t))
    await callback.answer()


@router.callback_query(F.data == "menu:about")
async def about(callback: CallbackQuery) -> None:
    t = await texts()
    body = f"<b>{t['aboutTitle']}</b>\n\n{t['aboutP1']}\n\n{t['aboutP2']}"
    await callback.message.answer(body, reply_markup=keyboards.about_menu(t))
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()
```

- [ ] **Step 6: portfolio.py**

```python
import logging

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery

from . import keyboards
from .backend import backend
from .menu import FALLBACK_ERROR, texts

router = Router()
log = logging.getLogger(__name__)


async def show_item(callback: CallbackQuery, idx: int) -> None:
    try:
        t = await texts()
        items = await backend.portfolio()
    except Exception:
        log.exception("backend unavailable")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    if not items:
        await callback.message.answer(t["botPortfolioEmpty"], reply_markup=keyboards.back_menu(t))
        await callback.answer()
        return
    idx = max(0, min(idx, len(items) - 1))
    item = items[idx]
    caption = f"<b>{item['title']}</b>\n\n{item['text']}"
    markup = keyboards.portfolio_nav(t, idx, len(items))
    try:
        data = await backend.image(item["image_path"])
        photo = BufferedInputFile(data, filename="case.png")
        await callback.message.answer_photo(photo, caption=caption, reply_markup=markup)
    except Exception:
        log.exception("image failed")
        await callback.message.answer(caption, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "menu:portfolio")
async def open_portfolio(callback: CallbackQuery) -> None:
    await show_item(callback, 0)


@router.callback_query(F.data.startswith("portfolio:"))
async def navigate(callback: CallbackQuery) -> None:
    idx = int(callback.data.split(":", 1)[1])
    await show_item(callback, idx)
```

- [ ] **Step 7: lead.py** - FSM:

```python
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from . import config, keyboards
from .backend import backend
from .menu import FALLBACK_ERROR, texts

router = Router()
log = logging.getLogger(__name__)

TYPE_LABELS = {"mvp": "MVP", "landing": "Лендинг", "webapp": "Веб-приложение", "support": "Поддержка"}


class LeadForm(StatesGroup):
    task = State()
    project_type = State()
    timeline = State()
    confirm = State()


@router.callback_query(F.data == "menu:lead")
async def start_lead(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await state.set_state(LeadForm.task)
    await callback.message.answer(t["botLeadAskTask"])
    await callback.answer()


@router.message(LeadForm.task)
async def got_task(message: Message, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(task=message.text or "")
    await state.set_state(LeadForm.project_type)
    await message.answer(t["botLeadAskType"], reply_markup=keyboards.lead_types(t))


@router.callback_query(LeadForm.project_type, F.data.startswith("lead_type:"))
async def got_type(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(project_type=callback.data.split(":", 1)[1])
    await state.set_state(LeadForm.timeline)
    await callback.message.answer(t["botLeadAskTimeline"])
    await callback.answer()


@router.message(LeadForm.timeline)
async def got_timeline(message: Message, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(timeline=message.text or "")
    data = await state.get_data()
    summary = (
        f"{t['botLeadConfirm']}\n\n"
        f"Задача: {data['task']}\n"
        f"Тип: {TYPE_LABELS.get(data['project_type'], data['project_type'])}\n"
        f"Сроки: {data['timeline']}"
    )
    await state.set_state(LeadForm.confirm)
    await message.answer(summary, reply_markup=keyboards.lead_confirm(t))


@router.callback_query(LeadForm.confirm, F.data == "lead:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await state.clear()
    await callback.message.answer(t["botLeadCancelled"], reply_markup=keyboards.main_menu(t))
    await callback.answer()


@router.callback_query(LeadForm.confirm, F.data == "lead:send")
async def send(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    data = await state.get_data()
    user = callback.from_user
    payload = {
        "tg_user_id": user.id,
        "username": user.username or "",
        "name": user.full_name,
        "task": data["task"],
        "project_type": data["project_type"],
        "timeline": data["timeline"],
    }
    try:
        ok = await backend.create_lead(payload)
    except Exception:
        log.exception("lead create failed")
        ok = False
    if not ok:
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    await state.clear()
    await callback.message.answer(t["botLeadThanks"], reply_markup=keyboards.main_menu(t))
    await callback.answer()
    if config.OWNER_CHAT_ID:
        contact = f"@{user.username}" if user.username else f"id {user.id}"
        summary = (
            f"Новая заявка\n"
            f"Имя: {user.full_name} ({contact})\n"
            f"Тип: {TYPE_LABELS.get(data['project_type'], data['project_type'])}\n"
            f"Сроки: {data['timeline']}\n\n"
            f"{data['task']}"
        )
        try:
            await callback.bot.send_message(config.OWNER_CHAT_ID, summary)
        except Exception:
            log.exception("owner notify failed")
```

- [ ] **Step 8: main.py**

```python
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from . import config, lead, menu, portfolio


async def run() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(lead.router)
    dp.include_router(portfolio.router)
    dp.include_router(menu.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
```

Порядок роутеров важен: lead с состояниями раньше menu.

- [ ] **Step 9: bot/Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml ./
COPY app app
RUN pip install --no-cache-dir .
CMD ["python", "-m", "app.main"]
```

- [ ] **Step 10: docker-compose.yml** - сервис:

```yaml
  bot:
    build: ./bot
    env_file: .env
    environment:
      BACKEND_URL: http://app:8000
    depends_on:
      - app
    restart: unless-stopped
```

- [ ] **Step 11: ci.yml** - в job backend после ruff бэкенда добавить шаг `- run: ruff check bot`.

- [ ] **Step 12: Локальная проверка** - venv для бота: `cd bot && python3 -m venv .venv && .venv/bin/pip install (nexus-индекс) -e ".[dev]" && .venv/bin/ruff check .`; запуск с локальным бэкендом: `BOT_TOKEN=<из .env> OWNER_CHAT_ID=<id> BACKEND_URL=http://127.0.0.1:8000 SERVICE_TOKEN=t1 .venv/bin/python -m app.main` - в логе Start polling, getMe ok.

- [ ] **Step 13: Коммит** `feat(bot): aiogram menu bot with lead form and portfolio`

---

### Task 6: Секреты, owner chat id, деплой, живая проверка

**Files:**
- Modify: `.env` на сервере (вне git), локальный `.env`; `README.md` (раздел про бота)

- [ ] **Step 1: OWNER_CHAT_ID** - пользователь пишет боту /start, затем: `curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | jq '.result[-1].message.chat.id'`.

- [ ] **Step 2: Локальный .env** - добавить BOT_TOKEN, OWNER_CHAT_ID, SERVICE_TOKEN=$(openssl rand -hex 32); `docker compose up -d --build` локально: лендинг 200, бот в логах polling, реальный /start от пользователя показывает меню.

- [ ] **Step 3: Серверный .env** - через ssh deploy добавить те же три переменные (SERVICE_TOKEN сгенерировать заново для прода).

- [ ] **Step 4: README** - раздел "Telegram-бот": назначение, env, как получить chat id.

- [ ] **Step 5: Пуш и деплой** - `git push origin main`, дождаться CI и Deploy, проверить: контейнер bot запущен (`docker compose ps` по ssh), лог polling без ошибок.

- [ ] **Step 6: Живой прогон по чек-листу спеки** (руками пользователя + моя проверка админки): /start, все разделы, листание портфолио, полная анкета, заявка в личке и в админке, смена статуса, добавление карточки с картинкой и её появление в боте.

---

## Итоговая проверка соответствия спеке

- Меню: /start, портфолио с листанием, услуги из svc-ключей, о студии со ссылкой - Task 5.
- Анкета 3 шага + подтверждение + отмена - Task 5 (lead.py).
- Заявки: личка владельца + база + админка со статусами - Task 1, 4, 5.
- Контент бота в базе, правится в админке - Task 3 (сид + миграция 007).
- Портфолио: таблица, CRUD, загрузка картинок, /uploads - Task 2, 4.
- Отдельный aiogram-сервис, polling, сервисный токен, без прямой записи в SQLite - Task 5.
- Ошибки: бэкенд недоступен -> вежливое сообщение, лог - Task 5.
- Никаких новых автотестов; существующие pytest зелёные на каждом коммите.
