"""Ingestion pipeline: collect real docs -> LLM-extract evidence -> store -> score."""

from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings
from ..services import rescore_leader
from .base import RawDoc
from .classify import extract_evidence
from .collectors import (
    collect_gdelt,
    collect_gnews,
    collect_newsapi,
    collect_wikipedia,
)
from .roster import LeaderSpec


def upsert_leader(db: Session, spec: LeaderSpec) -> models.Leader:
    leader = db.query(models.Leader).filter(models.Leader.name == spec.name).first()
    if leader is None:
        leader = models.Leader(name=spec.name)
        db.add(leader)
    leader.country = spec.country
    leader.region = spec.region
    leader.continent = spec.continent
    leader.political_affiliation = spec.political_affiliation
    leader.current = spec.current
    leader.bio = spec.bio or f"{spec.office}, {spec.country}. Evidence sourced from public records."
    db.commit()
    db.refresh(leader)
    return leader


def _collect_docs(spec: LeaderSpec, use_news: bool) -> list[RawDoc]:
    settings = get_settings()
    docs: list[RawDoc] = []
    for lang, title in spec.wikipedia:
        try:
            docs += collect_wikipedia(title, lang=lang)
        except Exception as exc:  # noqa: BLE001
            print(f"[wikipedia] {title} ({lang}) skipped: {type(exc).__name__}: {str(exc)[:80]}")
    if use_news:
        docs += collect_gdelt(spec.news_query, timespan=settings.ingest_timespan)
        docs += collect_gnews(spec.news_query)
        docs += collect_newsapi(spec.news_query)
    return docs


async def ingest_leader(db: Session, spec: LeaderSpec, *, use_news: bool = True) -> dict:
    settings = get_settings()
    leader = upsert_leader(db, spec)

    if not settings.llm_enabled:
        return {
            "leader": leader.name,
            "leader_id": leader.id,
            "error": "LLM not configured. Set LLM_API_KEY to classify real evidence.",
            "docs": 0,
            "evidence_added": 0,
        }

    docs = _collect_docs(spec, use_news)

    # Clean slate for this leader so re-runs are reproducible.
    db.query(models.Evidence).filter(models.Evidence.leader_id == leader.id).delete()
    db.commit()

    added = 0
    by_category: dict[str, int] = {}
    source_names: set[str] = set()
    for doc in docs:
        items = extract_evidence(spec.name, doc)
        for it in items:
            db.add(
                models.Evidence(
                    leader_id=leader.id,
                    category=it.category,
                    classification=it.classification,
                    polarity=it.polarity,
                    title=it.claim[:200],
                    extracted_text=it.claim,
                    source_name=doc.source_name,
                    source_url=doc.url,
                    source_rating=doc.source_rating,
                    published_at=it.date,
                )
            )
            added += 1
            by_category[it.category] = by_category.get(it.category, 0) + 1
            source_names.add(doc.source_name)
    db.commit()

    # Score from the freshly ingested, cited evidence.
    await rescore_leader(db, leader)

    return {
        "leader": leader.name,
        "leader_id": leader.id,
        "docs": len(docs),
        "sources": sorted(source_names),
        "evidence_added": added,
        "by_category": by_category,
    }
