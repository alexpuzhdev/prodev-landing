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
