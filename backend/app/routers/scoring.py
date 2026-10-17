from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import get_settings
from ..constants import (
    CATEGORIES,
    EVIDENCE_TYPES,
    SOURCE_RATINGS,
    TRUST_WEIGHTS,
)
from ..database import get_db
from ..services import rescore_leader

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


@router.post("/leader/{leader_id}", response_model=schemas.ScoreRunResult)
async def rescore(leader_id: int, db: Session = Depends(get_db)):
    leader = db.get(models.Leader, leader_id)
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found")
    results = await rescore_leader(db, leader)
    scored_by = "llm" if any(r.scored_by == "llm" for r in results) else "engine"
    return schemas.ScoreRunResult(
        leader_id=leader_id,
        scored_by=scored_by,
        categories_scored=len(results),
        scores=[schemas.CategoryScoreOut.model_validate(r) for r in results],
    )


@router.get("/methodology")
def methodology():
    """Exposes the complete scoring formula so users can inspect methodology."""
    settings = get_settings()
    return {
        "principle": (
            "AI assigns scores based on documented evidence and source weighting, "
            "not legal guilt."
        ),
        "categories": CATEGORIES,
        "score_values": {"positive": 1, "neutral": 0, "negative": -1},
        "trust_weights": TRUST_WEIGHTS,
        "evidence_classification_weights": EVIDENCE_TYPES,
        "source_ratings": SOURCE_RATINGS,
        "llm": {
            "enabled": settings.llm_enabled,
            "model": settings.llm_model if settings.llm_enabled else None,
        },
        "notes": [
            "Final confidence = 40% source quality + 25% source quantity + "
            "20% recency + 15% evidence consistency.",
            "Controversial categories discount single-source and unverified claims.",
            "Every score is reproducible from stored evidence via the deterministic engine.",
        ],
    }
