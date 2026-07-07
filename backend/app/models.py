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


class TerminalLine(Base):
    __tablename__ = "terminal_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(default=0)
    kind: Mapped[str] = mapped_column(default="ok")
    ru: Mapped[str] = mapped_column(default="")
    en: Mapped[str] = mapped_column(default="")
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)


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


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(default=0)
    title: Mapped[str] = mapped_column(default="")
    text: Mapped[str] = mapped_column(default="")
    image_path: Mapped[str] = mapped_column(default="")
    enabled: Mapped[bool] = mapped_column(default=True)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)
