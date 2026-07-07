import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from .auth import require_admin
from .db import get_db
from .models import PortfolioItem, utcnow

router = APIRouter(prefix="/api/portfolio")

ALLOWED_EXT = (".png", ".jpg", ".jpeg", ".webp")
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def uploads_dir(request: Request) -> Path:
    return request.app.state.uploads_dir


def _serialize(item: PortfolioItem) -> dict:
    return {
        "id": item.id,
        "position": item.position,
        "title": item.title,
        "text": item.text,
        "image_path": item.image_path,
        "enabled": item.enabled,
    }


async def _save_image(request: Request, image: UploadFile) -> str:
    ext = Path(image.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=422, detail="Картинка: png, jpg или webp")
    data = await image.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=422, detail="Картинка больше 5 МБ")
    name = f"{uuid.uuid4().hex}{ext}"
    (uploads_dir(request) / name).write_bytes(data)
    return f"/uploads/{name}"


def _delete_image(request: Request, image_path: str) -> None:
    name = Path(image_path).name
    file = uploads_dir(request) / name
    if name and file.is_file():
        file.unlink()


@router.get("")
def list_items(request: Request, all: int = 0, db: Session = Depends(get_db)):
    query = db.query(PortfolioItem)
    if all:
        require_admin(request)
    else:
        query = query.filter(PortfolioItem.enabled == True)  # noqa: E712
    items = query.order_by(PortfolioItem.position, PortfolioItem.id).all()
    return [_serialize(item) for item in items]


@router.post("", dependencies=[Depends(require_admin)])
async def create_item(
    request: Request,
    image: UploadFile,
    title: str = Form(""),
    text: str = Form(""),
    position: int = Form(0),
    db: Session = Depends(get_db),
):
    image_path = await _save_image(request, image)
    item = PortfolioItem(title=title, text=text, position=position, image_path=image_path)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.put("/{item_id}", dependencies=[Depends(require_admin)])
async def update_item(
    request: Request,
    item_id: int,
    image: UploadFile | None = None,
    title: str = Form(""),
    text: str = Form(""),
    position: int = Form(0),
    enabled: int = Form(1),
    db: Session = Depends(get_db),
):
    item = db.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Карточка не найдена")
    if image is not None and image.filename:
        _delete_image(request, item.image_path)
        item.image_path = await _save_image(request, image)
    item.title = title
    item.text = text
    item.position = position
    item.enabled = bool(enabled)
    item.updated_at = utcnow()
    db.commit()
    return _serialize(item)


@router.delete("/{item_id}", dependencies=[Depends(require_admin)])
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = db.get(PortfolioItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Карточка не найдена")
    _delete_image(request, item.image_path)
    db.delete(item)
    db.commit()
    return {"ok": True}
