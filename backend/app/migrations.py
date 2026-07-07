"""Миграции данных: применяются на старте, каждая ровно один раз."""

from datetime import datetime

from sqlalchemy.orm import Mapped, Session, mapped_column

from .models import Base, Content, utcnow


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


MIGRATIONS = [
    ("001_rebrand_atrice", _001_rebrand_atrice),
    ("002_strip_ai_markers", _002_strip_ai_markers),
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
