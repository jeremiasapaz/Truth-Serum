"""Seed the real roster into the leaders table so real names show immediately.

Scores start neutral (0, 0% confidence, "no evidence yet") until evidence is
ingested with an LLM key. Also purges the fictional demo leaders so the
Dashboard/Compare tabs show only real people.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models
from ..constants import CATEGORIES
from ..scoring import compute_score
from .roster import ROSTER

# Fictional countries used by the original demo seed.
SYNTHETIC_COUNTRIES = {"Maravia", "Veldoria", "Keshima", "Rusalka", "Zahran", "Solterra"}


def ensure_real_leaders(db: Session) -> None:
    # Remove fictional demo leaders (cascade removes their evidence + scores).
    demo = (
        db.query(models.Leader)
        .filter(models.Leader.country.in_(SYNTHETIC_COUNTRIES))
        .all()
    )
    for leader in demo:
        db.delete(leader)
    if demo:
        db.commit()

    existing = {name for (name,) in db.query(models.Leader.name).all()}
    for spec in ROSTER.values():
        if spec.name in existing:
            continue
        leader = models.Leader(
            name=spec.name, country=spec.country, region=spec.region,
            continent=spec.continent, political_affiliation=spec.political_affiliation,
            current=spec.current,
            bio=f"{spec.office}, {spec.country}. Awaiting evidence ingestion "
                "(run the pipeline with an LLM key to populate cited scores).",
        )
        db.add(leader)
        db.flush()
        for category in CATEGORIES:
            r = compute_score(category, [])  # neutral: no evidence yet
            db.add(models.CategoryScore(
                leader_id=leader.id, category=category, score=r.score,
                confidence=r.confidence, evidence_count=0, source_count=0,
                source_quality=0.0, reason=r.reason, scored_by="engine",
            ))
    db.commit()
