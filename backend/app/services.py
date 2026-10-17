"""Service helpers: aggregate scores and run (re)scoring for a leader."""

from __future__ import annotations

from sqlalchemy.orm import Session

from . import models
from .constants import CATEGORIES
from .llm import score_with_llm


def evidence_to_dict(e: models.Evidence) -> dict:
    return {
        "classification": e.classification,
        "polarity": e.polarity,
        "title": e.title,
        "extracted_text": e.extracted_text,
        "source_name": e.source_name,
        "source_rating": e.source_rating,
        "published_at": e.published_at,
    }


async def rescore_leader(db: Session, leader: models.Leader) -> list[models.CategoryScore]:
    """Recompute every category score for a leader and persist + version them."""
    results: list[models.CategoryScore] = []

    by_cat: dict[str, list[models.Evidence]] = {c: [] for c in CATEGORIES}
    for ev in leader.evidence:
        by_cat.setdefault(ev.category, []).append(ev)

    # Wipe old scores for this leader; keep history table intact.
    db.query(models.CategoryScore).filter(
        models.CategoryScore.leader_id == leader.id
    ).delete()

    for category in CATEGORIES:
        ev_list = by_cat.get(category, [])
        result = await score_with_llm(
            leader_name=leader.name,
            category=category,
            evidence_dicts=[evidence_to_dict(e) for e in ev_list],
        )
        scored_by = "llm" if result.components.get("llm_model") else "engine"

        cs = models.CategoryScore(
            leader_id=leader.id,
            category=category,
            score=result.score,
            confidence=result.confidence,
            evidence_count=result.evidence_count,
            source_count=result.source_count,
            source_quality=result.source_quality,
            reason=result.reason,
            scored_by=scored_by,
        )
        db.add(cs)
        db.add(
            models.ScoreHistory(
                leader_id=leader.id,
                category=category,
                score=result.score,
                confidence=result.confidence,
            )
        )
        results.append(cs)

    db.commit()
    for cs in results:
        db.refresh(cs)
    return results


def leader_aggregates(leader: models.Leader) -> dict:
    """Total score, average confidence and evidence totals from stored scores."""
    scores = leader.scores
    evidence_total = len(leader.evidence)
    if not scores:
        return {"total_score": 0.0, "avg_confidence": 0.0, "evidence_total": evidence_total}

    # Total score: confidence-weighted average of category scores, scaled to -100..100.
    num = sum(s.score * (s.confidence / 100.0) for s in scores)
    den = sum((s.confidence / 100.0) for s in scores) or 1.0
    total = (num / den) * 100.0
    avg_conf = sum(s.confidence for s in scores) / len(scores)
    return {
        "total_score": round(total, 1),
        "avg_confidence": round(avg_conf, 1),
        "evidence_total": evidence_total,
    }
