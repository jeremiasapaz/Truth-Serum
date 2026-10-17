"""Ingestion pipeline: collect real docs -> LLM-extract evidence -> store -> score."""

from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings
from ..services import rescore_leader
from .base import RawDoc
from .classify import classify_articles, extract_evidence
from .collectors import (
    collect_bing_news,
    collect_currents,
    collect_gdelt,
    collect_gnews,
    collect_google_news,
    collect_mediastack,
    collect_newsapi,
    collect_newsdata,
    collect_rss_feeds,
    collect_wikipedia,
)
from .feeds import feeds_for
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


def _dedupe(docs: list[RawDoc]) -> list[RawDoc]:
    """Drop exact-duplicate articles (same URL, or same source+title)."""
    seen: set[tuple] = set()
    out: list[RawDoc] = []
    for d in docs:
        key = (d.url.split("?")[0], d.source_name, d.title.lower()[:90])
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def _collect_docs(spec: LeaderSpec, use_news: bool) -> list[RawDoc]:
    settings = get_settings()
    docs: list[RawDoc] = []

    # Wikipedia (primary cited source)
    for lang, title in spec.wikipedia:
        try:
            docs += collect_wikipedia(title, lang=lang)
        except Exception as exc:  # noqa: BLE001
            print(f"[wikipedia] {title} ({lang}) skipped: {type(exc).__name__}: {str(exc)[:80]}")

    if use_news:
        # Keyless aggregators (local + foreign press/magazines across many outlets)
        docs += collect_google_news(spec.news_query, locales=spec.locales())
        docs += collect_bing_news(spec.news_query)
        # Direct outlet / TV broadcaster feeds (first-party corroboration)
        docs += collect_rss_feeds(feeds_for(spec.continent), spec.terms())
        # Keyless news index (blocked on some networks)
        docs += collect_gdelt(spec.news_query, timespan=settings.ingest_timespan)
        # Keyed aggregators (each spans many outlets) — active only if keys set
        docs += collect_gnews(spec.news_query)
        docs += collect_newsapi(spec.news_query)
        docs += collect_newsdata(spec.news_query)
        docs += collect_mediastack(spec.news_query)
        docs += collect_currents(spec.news_query)

    return _dedupe(docs)


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
    # Cross-source dedupe of near-identical claims from the SAME source (keeps
    # the same claim from DIFFERENT sources, which is genuine corroboration).
    claim_seen: set[tuple] = set()

    def _store(doc, it):
        nonlocal added
        key = (doc.source_name, it.category, it.polarity, it.claim.lower()[:70])
        if key in claim_seen:
            return
        claim_seen.add(key)
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

    documents = [d for d in docs if d.kind == "document"]
    articles = [d for d in docs if d.kind != "document"]

    # Long documents (e.g. Wikipedia): full chunked extraction.
    for doc in documents:
        for it in extract_evidence(spec.name, doc):
            _store(doc, it)
    # Short news articles: efficient batched classification.
    for doc, it in classify_articles(spec.name, articles):
        _store(doc, it)
    db.commit()

    # Score from the freshly ingested, cited evidence.
    await rescore_leader(db, leader)

    return {
        "leader": leader.name,
        "leader_id": leader.id,
        "docs": len(docs),
        "documents": len(documents),
        "articles": len(articles),
        "source_count": len(source_names),
        "sources": sorted(source_names),
        "evidence_added": added,
        "by_category": by_category,
    }
