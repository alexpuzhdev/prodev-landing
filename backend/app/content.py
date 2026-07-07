from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import Content

router = APIRouter(prefix="/api/content")


@router.get("")
def get_content(db: Session = Depends(get_db)):
    rows = db.query(Content).all()
    return {
        r.key: {"ru": r.ru, "en": r.en, "label": r.label, "section": r.section} for r in rows
    }
