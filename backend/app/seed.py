import json
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Content, TerminalLine


def seed_terminal_if_empty(session: Session, seed_path: Path) -> int:
    if session.query(TerminalLine).count() > 0:
        return 0
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    for i, line in enumerate(data):
        session.add(
            TerminalLine(position=(i + 1) * 10, kind=line["kind"], ru=line["ru"], en=line["en"])
        )
    session.commit()
    return len(data)


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
