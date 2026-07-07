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
