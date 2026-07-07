from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import require_admin
from .db import get_db
from .models import TerminalLine, utcnow

router = APIRouter(prefix="/api/terminal")

KINDS = ("cmd", "ok", "info")


class TerminalLineBody(BaseModel):
    kind: str
    ru: str
    en: str


def _serialize(line: TerminalLine) -> dict:
    return {
        "id": line.id,
        "position": line.position,
        "kind": line.kind,
        "ru": line.ru,
        "en": line.en,
    }


def _validate_kind(kind: str) -> None:
    if kind not in KINDS:
        raise HTTPException(status_code=422, detail="kind должен быть cmd, ok или info")


@router.get("")
def list_lines(db: Session = Depends(get_db)):
    lines = db.query(TerminalLine).order_by(TerminalLine.position, TerminalLine.id).all()
    return [_serialize(line) for line in lines]


@router.post("", dependencies=[Depends(require_admin)])
def create_line(body: TerminalLineBody, db: Session = Depends(get_db)):
    _validate_kind(body.kind)
    max_pos = db.query(func.max(TerminalLine.position)).scalar() or 0
    line = TerminalLine(position=max_pos + 10, kind=body.kind, ru=body.ru, en=body.en)
    db.add(line)
    db.commit()
    db.refresh(line)
    return _serialize(line)


@router.put("/{line_id}", dependencies=[Depends(require_admin)])
def update_line(line_id: int, body: TerminalLineBody, db: Session = Depends(get_db)):
    _validate_kind(body.kind)
    line = db.get(TerminalLine, line_id)
    if line is None:
        raise HTTPException(status_code=404, detail="Строка не найдена")
    line.kind = body.kind
    line.ru = body.ru
    line.en = body.en
    line.updated_at = utcnow()
    db.commit()
    return _serialize(line)


@router.delete("/{line_id}", dependencies=[Depends(require_admin)])
def delete_line(line_id: int, db: Session = Depends(get_db)):
    line = db.get(TerminalLine, line_id)
    if line is None:
        raise HTTPException(status_code=404, detail="Строка не найдена")
    db.delete(line)
    db.commit()
    return {"ok": True}
