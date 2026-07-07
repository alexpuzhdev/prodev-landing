from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import require_admin
from .db import get_db
from .models import Lead

router = APIRouter(prefix="/api/leads")

STATUSES = ("new", "done")


class LeadCreate(BaseModel):
    tg_user_id: int
    username: str = ""
    name: str = ""
    task: str
    project_type: str
    timeline: str


class LeadPatch(BaseModel):
    status: str


def require_service_token(request: Request) -> None:
    expected = request.app.state.service_token
    if not expected or request.headers.get("x-service-token") != expected:
        raise HTTPException(status_code=401, detail="Неверный сервисный токен")


def _serialize(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "tg_user_id": lead.tg_user_id,
        "username": lead.username,
        "name": lead.name,
        "task": lead.task,
        "project_type": lead.project_type,
        "timeline": lead.timeline,
        "status": lead.status,
        "created_at": lead.created_at.isoformat(),
    }


@router.post("", dependencies=[Depends(require_service_token)])
def create_lead(body: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        tg_user_id=body.tg_user_id,
        username=body.username,
        name=body.name,
        task=body.task,
        project_type=body.project_type,
        timeline=body.timeline,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"id": lead.id}


@router.get("", dependencies=[Depends(require_admin)])
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc(), Lead.id.desc()).all()
    return [_serialize(lead) for lead in leads]


@router.patch("/{lead_id}", dependencies=[Depends(require_admin)])
def patch_lead(lead_id: int, body: LeadPatch, db: Session = Depends(get_db)):
    if body.status not in STATUSES:
        raise HTTPException(status_code=422, detail="status: new или done")
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    lead.status = body.status
    db.commit()
    return _serialize(lead)
