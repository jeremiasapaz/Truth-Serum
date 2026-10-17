from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..constants import CATEGORIES
from ..database import get_db
from ..services import leader_aggregates

router = APIRouter(prefix="/api/leaders", tags=["leaders"])


def _summary(leader: models.Leader) -> schemas.LeaderSummary:
    agg = leader_aggregates(leader)
    return schemas.LeaderSummary(
        id=leader.id,
        name=leader.name,
        country=leader.country,
        region=leader.region,
        continent=leader.continent,
        political_affiliation=leader.political_affiliation,
        current=leader.current,
        photo_url=leader.photo_url,
        **agg,
    )


SORTS = {
    "name",
    "total_score_desc",
    "total_score_asc",
    "confidence_desc",
    "confidence_asc",
    "most_evidence",
    "most_scandals",
    "most_investigated",
    "most_controversial",
    "highest_corruption",
    "lowest_corruption",
    "highest_environmental",
    "lowest_environmental",
    "most_human_rights",
    "most_democratic_integrity",
    "most_court_documents",
}


@router.get("", response_model=list[schemas.LeaderSummary])
def list_leaders(
    db: Session = Depends(get_db),
    country: str | None = None,
    region: str | None = None,
    continent: str | None = None,
    political_affiliation: str | None = None,
    current: bool | None = None,
    polarity: str | None = Query(None, description="positive|negative|neutral"),
    keyword: str | None = None,
    score_min: float | None = None,
    score_max: float | None = None,
    confidence_min: float | None = None,
    confidence_max: float | None = None,
    sort: str = "total_score_desc",
    limit: int = 200,
):
    q = db.query(models.Leader)
    if country:
        q = q.filter(models.Leader.country == country)
    if region:
        q = q.filter(models.Leader.region == region)
    if continent:
        q = q.filter(models.Leader.continent == continent)
    if political_affiliation:
        q = q.filter(models.Leader.political_affiliation == political_affiliation)
    if current is not None:
        q = q.filter(models.Leader.current == (1 if current else 0))
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            models.Leader.name.ilike(like) | models.Leader.bio.ilike(like)
        )

    leaders = q.all()
    summaries = [_summary(ld) for ld in leaders]
    lookup = {ld.id: ld for ld in leaders}

    # Range filters operate on computed aggregates.
    if score_min is not None:
        summaries = [s for s in summaries if s.total_score >= score_min]
    if score_max is not None:
        summaries = [s for s in summaries if s.total_score <= score_max]
    if confidence_min is not None:
        summaries = [s for s in summaries if s.avg_confidence >= confidence_min]
    if confidence_max is not None:
        summaries = [s for s in summaries if s.avg_confidence <= confidence_max]
    if polarity == "positive":
        summaries = [s for s in summaries if s.total_score > 5]
    elif polarity == "negative":
        summaries = [s for s in summaries if s.total_score < -5]
    elif polarity == "neutral":
        summaries = [s for s in summaries if -5 <= s.total_score <= 5]

    _apply_sort(summaries, lookup, sort)
    return summaries[:limit]


def _cat_score(leader: models.Leader, category: str) -> int:
    for s in leader.scores:
        if s.category == category:
            return s.score
    return 0


def _count_negative(leader: models.Leader) -> int:
    return sum(1 for s in leader.scores if s.score < 0)


def _count_investigations(leader: models.Leader) -> int:
    return sum(
        1
        for e in leader.evidence
        if e.classification in ("ONGOING INVESTIGATION", "COURT RECORD")
    )


def _count_court_docs(leader: models.Leader) -> int:
    return sum(1 for e in leader.evidence if e.classification == "COURT RECORD")


def _count_scandals(leader: models.Leader) -> int:
    return sum(1 for e in leader.evidence if e.category == "Scandals")


def _apply_sort(summaries, lookup, sort):
    if sort not in SORTS:
        sort = "total_score_desc"

    def key(s):
        ld = lookup[s.id]
        return {
            "name": s.name.lower(),
            "total_score_desc": -s.total_score,
            "total_score_asc": s.total_score,
            "confidence_desc": -s.avg_confidence,
            "confidence_asc": s.avg_confidence,
            "most_evidence": -s.evidence_total,
            "most_scandals": -_count_scandals(ld),
            "most_investigated": -_count_investigations(ld),
            "most_controversial": -_count_negative(ld),
            "most_court_documents": -_count_court_docs(ld),
            "highest_corruption": _cat_score(ld, "Corruption"),
            "lowest_corruption": -_cat_score(ld, "Corruption"),
            "highest_environmental": -_cat_score(ld, "Environmental Crime"),
            "lowest_environmental": _cat_score(ld, "Environmental Crime"),
            "most_human_rights": _cat_score(ld, "Human Rights"),
            "most_democratic_integrity": -_cat_score(ld, "Democratic Integrity"),
        }[sort]

    summaries.sort(key=key)


@router.get("/filters/options")
def filter_options(db: Session = Depends(get_db)):
    def distinct(col):
        return [r[0] for r in db.query(col).distinct().all() if r[0]]

    return {
        "countries": sorted(distinct(models.Leader.country)),
        "regions": sorted(distinct(models.Leader.region)),
        "continents": sorted(distinct(models.Leader.continent)),
        "affiliations": sorted(distinct(models.Leader.political_affiliation)),
        "categories": CATEGORIES,
        "sorts": sorted(SORTS),
    }


@router.get("/{leader_id}", response_model=schemas.LeaderDetail)
def get_leader(leader_id: int, db: Session = Depends(get_db)):
    leader = db.get(models.Leader, leader_id)
    if not leader:
        raise HTTPException(status_code=404, detail="Leader not found")
    agg = leader_aggregates(leader)
    scores = sorted(leader.scores, key=lambda s: CATEGORIES.index(s.category) if s.category in CATEGORIES else 99)
    return schemas.LeaderDetail(
        id=leader.id,
        name=leader.name,
        country=leader.country,
        region=leader.region,
        continent=leader.continent,
        political_affiliation=leader.political_affiliation,
        current=leader.current,
        photo_url=leader.photo_url,
        bio=leader.bio,
        scores=[schemas.CategoryScoreOut.model_validate(s) for s in scores],
        **agg,
    )
