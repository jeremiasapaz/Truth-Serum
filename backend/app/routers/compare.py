from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models
from ..constants import CATEGORIES
from ..database import get_db
from ..services import leader_aggregates

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.get("")
def compare(
    ids: list[int] = Query(..., description="Leader ids, up to 10"),
    db: Session = Depends(get_db),
):
    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Compare at most 10 leaders")

    leaders = db.query(models.Leader).filter(models.Leader.id.in_(ids)).all()
    if not leaders:
        raise HTTPException(status_code=404, detail="No leaders found")

    order = {lid: i for i, lid in enumerate(ids)}
    leaders.sort(key=lambda ld: order.get(ld.id, 99))

    out = []
    for ld in leaders:
        agg = leader_aggregates(ld)
        score_map = {s.category: s for s in ld.scores}
        out.append(
            {
                "id": ld.id,
                "name": ld.name,
                "country": ld.country,
                "political_affiliation": ld.political_affiliation,
                "total_score": agg["total_score"],
                "avg_confidence": agg["avg_confidence"],
                "categories": {
                    c: {
                        "score": (score_map[c].score if c in score_map else 0),
                        "confidence": (score_map[c].confidence if c in score_map else 0.0),
                    }
                    for c in CATEGORIES
                },
            }
        )

    return {"categories": CATEGORIES, "leaders": out}


@router.get("/trend/{leader_id}")
def trend(leader_id: int, category: str | None = None, db: Session = Depends(get_db)):
    """Score history over time for trend charts."""
    q = db.query(models.ScoreHistory).filter(
        models.ScoreHistory.leader_id == leader_id
    )
    if category:
        q = q.filter(models.ScoreHistory.category == category)
    rows = q.order_by(models.ScoreHistory.created_at.asc()).all()
    return [
        {
            "category": r.category,
            "score": r.score,
            "confidence": r.confidence,
            "at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
