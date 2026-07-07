"""Миграции данных: применяются на старте, каждая ровно один раз."""

import json
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Mapped, Session, mapped_column

from .models import Base, Content, TerminalLine, utcnow

BACKEND_DIR = Path(__file__).resolve().parent.parent


class AppliedMigration(Base):
    __tablename__ = "applied_migrations"

    id: Mapped[str] = mapped_column(primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(default=utcnow)


def _001_rebrand_atrice(session: Session) -> None:
    """Ребрендинг: prodev.team -> atrice во всех текстах."""
    exact = {
        "brandName": ("atrice", "atrice"),
        "termTitle": ("atrice - deploy", "atrice - deploy"),
        "footCopyright": ("© 2026 atrice", "© 2026 atrice"),
    }
    for key, (ru, en) in exact.items():
        row = session.get(Content, key)
        if row is not None:
            row.ru, row.en = ru, en
            row.updated_at = utcnow()
    for row in session.query(Content).all():
        if "prodev.team" in row.ru or "prodev.team" in row.en:
            row.ru = row.ru.replace("prodev.team", "atrice")
            row.en = row.en.replace("prodev.team", "atrice")
            row.updated_at = utcnow()


def _002_strip_ai_markers(session: Session) -> None:
    """Убирает тире и умные кавычки из текстов лендинга."""
    replacements = {"—": "-", "«": '"', "»": '"', "“": '"', "”": '"'}
    fields = ("ru", "en", "label", "section")
    for row in session.query(Content).all():
        changed = False
        for field in fields:
            value = getattr(row, field)
            new_value = value
            for old, new in replacements.items():
                new_value = new_value.replace(old, new)
            if new_value != value:
                setattr(row, field, new_value)
                changed = True
        if changed:
            row.updated_at = utcnow()


def _003_terminal_lines(session: Session) -> None:
    """Переносит сценарий терминала из content в таблицу terminal_lines."""
    if session.query(TerminalLine).count() > 0:
        return
    moved = ["termScope", "termStack1", "termStack2", "termTests", "termDeploying", "termLive"]
    rows = {key: session.get(Content, key) for key in moved}
    if not any(rows.values()):
        return
    plan = [
        ("cmd", None, "git clone your-idea && cd your-idea", "git clone your-idea && cd your-idea"),
        ("ok", "termScope", "скоуп и оценка - 1 день", "scope & estimate - 1 day"),
        ("cmd", None, "npm run build", "npm run build"),
        ("ok", "termStack1", "frontend · react + typescript", "frontend · react + typescript"),
        ("ok", "termStack2", "backend · node + postgres", "backend · node + postgres"),
        ("ok", "termTests", "тесты пройдены (128/128)", "tests passed (128/128)"),
        ("cmd", None, "npm run deploy --production", "npm run deploy --production"),
        ("info", "termDeploying", "деплой в продакшен…", "deploying to production…"),
        (
            "ok",
            "termLive",
            "запущено: от идеи до продакшена за недели, не месяцы",
            "live: from idea to production in weeks, not months",
        ),
    ]
    for i, (kind, key, ru, en) in enumerate(plan):
        row = rows.get(key) if key else None
        if row is not None:
            ru, en = row.ru, row.en
        session.add(TerminalLine(position=(i + 1) * 10, kind=kind, ru=ru, en=en))
    for row in rows.values():
        if row is not None:
            session.delete(row)


def _004_copy_update(session: Session) -> None:
    """Копирайтинг: тексты конкретнее и ближе к пользе клиента."""
    texts = {
        "heroText": (
            "Проектируем, разрабатываем и запускаем веб-приложения, лендинги и MVP. "
            "Берём весь цикл на себя: от первого созвона до продукта, которым пользуются.",
            "We design, build and launch web apps, landing pages and MVPs. "
            "We own the full cycle: from the first call to a product in your users' hands.",
        ),
        "aboutP1": (
            "Мы небольшая команда разработчиков и дизайнера. Ведём проект от старта до "
            "продакшена без посредников: вы говорите напрямую с теми, кто пишет код.",
            "We are a small team of developers and a designer. We take a project from "
            "kick-off to production with no middlemen: you talk directly to the people "
            "writing the code.",
        ),
        "aboutP2": (
            "Работаем короткими итерациями: сперва версия, которую можно показать "
            "пользователям, дальше развитие на основе реальных данных. Сроки и объём "
            "фиксируем до старта и держим слово.",
            "We work in short iterations: first a version you can put in front of users, "
            "then improvements driven by real data. Scope and timeline are agreed before "
            "we start, and we keep our word.",
        ),
        "svc1Text": (
            "Доведём идею до продукта, который не стыдно показать инвесторам и первым "
            "пользователям. Архитектура, разработка и запуск в согласованные сроки.",
            "We turn an idea into a product you can confidently show investors and first "
            "users. Architecture, development and launch within an agreed timeline.",
        ),
        "svc2Text": (
            "Страницы, которые понятно доносят оффер и приводят заявки: запуск продукта, "
            "услуга, портфолио. Вёрстка, формы и аналитика включены.",
            "Pages that state your offer clearly and bring in leads: product launches, "
            "services, portfolios. Markup, forms and analytics included.",
        ),
        "svc3Text": (
            "Личные кабинеты, админки и внутренние инструменты. Фронтенд и бэкенд из "
            "одних рук: авторизация, база данных, интеграции.",
            "Dashboards, admin panels and internal tools. Frontend and backend from one "
            "team: auth, database, integrations.",
        ),
        "svc4Text": (
            "Возьмём существующий проект: починим баги, ускорим и добавим "
            "функциональность. Аудит кода перед стартом бесплатный.",
            "We take over existing projects: fix bugs, improve performance, add features. "
            "The code audit before we start is free.",
        ),
        "ctaText": (
            "Опишите задачу в паре предложений. В течение дня вернёмся с оценкой "
            "сроков и стоимости.",
            "Describe your task in a couple of sentences. Within a day we will get back "
            "with a time and cost estimate.",
        ),
    }
    for key, (ru, en) in texts.items():
        row = session.get(Content, key)
        if row is not None:
            row.ru = ru
            row.en = en
            row.updated_at = utcnow()


def _005_copy_polish(session: Session) -> None:
    """Правка текстов: естественнее формулировки, упор на доверие без давления."""
    texts = {
        "heroText": (
            "Проектируем, разрабатываем и запускаем веб-приложения, лендинги и MVP. "
            "Ведём проект целиком: от постановки задачи до работающего продукта.",
            "We design, build and launch web apps, landing pages and MVPs. "
            "We run the project end to end: from scoping the task to a working product.",
        ),
        "aboutP1": (
            "Ведём проект прозрачно: регулярные демо, понятные статусы и один "
            "ответственный за результат. Если удобнее обсуждать детали напрямую с "
            "разработчиками и дизайнером, такая возможность всегда есть.",
            "We keep the project transparent: regular demos, clear status updates and "
            "one person responsible for the result. And if you prefer to discuss details "
            "directly with the developers and the designer, that option is always there.",
        ),
        "aboutP2": (
            "Работаем итерациями: сначала версия, которую можно показать пользователям, "
            "затем развитие на основе реальных данных. Объём и сроки фиксируем до старта "
            "и не двигаем их по ходу.",
            "We work in iterations: first a version you can show to users, then "
            "improvements based on real data. Scope and deadlines are fixed before we "
            "start and stay fixed.",
        ),
        "svc1Text": (
            "Поможем довести идею до продукта, который можно показывать инвесторам и "
            "первым пользователям. Архитектура, разработка и запуск в согласованные "
            "сроки.",
            "We help turn an idea into a product ready to show investors and first "
            "users. Architecture, development and launch within the agreed timeline.",
        ),
        "svc2Text": (
            "Страницы, которые ясно объясняют продукт и приводят заявки: запуск, услуга, "
            "портфолио. Вёрстка, формы и аналитика входят в работу.",
            "Pages that explain your product clearly and bring in leads: launches, "
            "services, portfolios. Markup, forms and analytics are part of the job.",
        ),
        "svc3Text": (
            "Личные кабинеты, админки и внутренние инструменты. Фронтенд и бэкенд делает "
            "одна команда: авторизация, база данных, интеграции.",
            "Dashboards, admin panels and internal tools. One team builds both frontend "
            "and backend: auth, database, integrations.",
        ),
        "svc4Text": (
            "Возьмём существующий проект: исправим баги, ускорим работу и добавим новые "
            "функции. Начинаем с бесплатного аудита кода.",
            "We take over existing projects: fix bugs, speed things up and add features. "
            "We start with a free code audit.",
        ),
    }
    for key, (ru, en) in texts.items():
        row = session.get(Content, key)
        if row is not None:
            row.ru = ru
            row.en = en
            row.updated_at = utcnow()


def _006_stack_and_terminal(session: Session) -> None:
    """Стек без свалки брендов, терминал согласован с python-бэкендом."""
    stack = {
        "stackBackItems": "Python · PHP · PostgreSQL · Redis",
        "stackInfraItems": "Docker · GitHub Actions · nginx",
    }
    for key, value in stack.items():
        row = session.get(Content, key)
        if row is not None:
            row.ru = value
            row.en = value
            row.updated_at = utcnow()
    lines = {
        "backend · node + postgres": (
            "ok",
            "backend · python + postgresql",
            "backend · python + postgresql",
        ),
        "тесты пройдены (128/128)": (
            "ok",
            "uvicorn запущен на :8000",
            "uvicorn running on :8000",
        ),
    }
    for old_ru, (kind, ru, en) in lines.items():
        for line in session.query(TerminalLine).filter(TerminalLine.ru == old_ru).all():
            line.kind = kind
            line.ru = ru
            line.en = en
            line.updated_at = utcnow()


def _007_bot_content(session: Session) -> None:
    """Добавляет тексты Telegram-бота в существующие базы."""
    seed_path = Path(
        os.environ.get("SEED_PATH", BACKEND_DIR.parent / "shared" / "seed_content.json")
    )
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    for key, row in data.items():
        if row.get("section") != "Бот" or session.get(Content, key) is not None:
            continue
        session.add(
            Content(
                key=key, ru=row["ru"], en=row["en"], label=row.get("label", key), section="Бот"
            )
        )


MIGRATIONS = [
    ("001_rebrand_atrice", _001_rebrand_atrice),
    ("002_strip_ai_markers", _002_strip_ai_markers),
    ("003_terminal_lines", _003_terminal_lines),
    ("004_copy_update", _004_copy_update),
    ("005_copy_polish", _005_copy_polish),
    ("006_stack_and_terminal", _006_stack_and_terminal),
    ("007_bot_content", _007_bot_content),
]


def run_migrations(session: Session) -> list[str]:
    applied = {m.id for m in session.query(AppliedMigration).all()}
    ran = []
    for mig_id, func in MIGRATIONS:
        if mig_id in applied:
            continue
        func(session)
        session.add(AppliedMigration(id=mig_id))
        session.commit()
        ran.append(mig_id)
    return ran
