"""Миграции данных: применяются на старте, каждая ровно один раз."""

from datetime import datetime

from sqlalchemy.orm import Mapped, Session, mapped_column

from .models import Base, Content, TerminalLine, utcnow


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


MIGRATIONS = [
    ("001_rebrand_atrice", _001_rebrand_atrice),
    ("002_strip_ai_markers", _002_strip_ai_markers),
    ("003_terminal_lines", _003_terminal_lines),
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
