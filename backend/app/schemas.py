from datetime import datetime

from pydantic import BaseModel


class EvidenceOut(BaseModel):
    id: int
    category: str
    classification: str
    polarity: int
    title: str
    extracted_text: str | None
    source_name: str
    source_url: str | None
    source_rating: float
    published_at: datetime | None
    created_at: datetime | None

    class Config:
        from_attributes = True


class CategoryScoreOut(BaseModel):
    category: str
    score: int
    confidence: float
    evidence_count: int
    source_count: int
    source_quality: float
    reason: str | None
    scored_by: str

    class Config:
        from_attributes = True


class LeaderSummary(BaseModel):
    id: int
    name: str
    country: str | None
    region: str | None
    continent: str | None
    political_affiliation: str | None
    current: int
    photo_url: str | None
    total_score: float = 0.0
    avg_confidence: float = 0.0
    evidence_total: int = 0

    class Config:
        from_attributes = True


class LeaderDetail(LeaderSummary):
    bio: str | None = None
    scores: list[CategoryScoreOut] = []


class ScoreRunResult(BaseModel):
    leader_id: int
    scored_by: str
    categories_scored: int
    scores: list[CategoryScoreOut]
