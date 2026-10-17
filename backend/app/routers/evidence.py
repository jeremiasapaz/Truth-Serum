from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.get("/leader/{leader_id}", response_model=list[schemas.EvidenceOut])
def evidence_for_leader(
    leader_id: int, category: str | None = None, db: Session = Depends(get_db)
):
    leader = db.get(models.Leader, leader_id)
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found")
    q = db.query(models.Evidence).filter(models.Evidence.leader_id == leader_id)
    if category:
        q = q.filter(models.Evidence.category == category)
    return q.order_by(models.Evidence.published_at.desc().nullslast()).all()


@router.get("/{evidence_id}", response_model=schemas.EvidenceOut)
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    ev = db.get(models.Evidence, evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return ev
