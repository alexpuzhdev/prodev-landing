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
