from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Leader(Base):
    __tablename__ = "leaders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    country = Column(String, index=True)
    region = Column(String, index=True)
    continent = Column(String, index=True)
    political_affiliation = Column(String, index=True)
    current = Column(Integer, default=1)  # 1 = current leader, 0 = former
    photo_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    evidence = relationship(
        "Evidence", back_populates="leader", cascade="all, delete-orphan"
    )
    scores = relationship(
        "CategoryScore", back_populates="leader", cascade="all, delete-orphan"
    )


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    url = Column(String, nullable=True)
    rating = Column(Float, default=0.5)  # 0..1 reliability


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=False)
    category = Column(String, index=True, nullable=False)

    # Evidence classification tag, e.g. "COURT RECORD", "UNVERIFIED CLAIM".
    classification = Column(String, nullable=False)

    # Direction this evidence pushes the category score: -1, 0, +1.
    polarity = Column(Integer, default=0)

    title = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)

    source_name = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    source_rating = Column(Float, default=0.5)

    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    leader = relationship("Leader", back_populates="evidence")


class CategoryScore(Base):
    __tablename__ = "category_scores"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=False)
    category = Column(String, index=True, nullable=False)

    score = Column(Integer, default=0)          # -1 / 0 / +1
    confidence = Column(Float, default=0.0)      # 0..100
    evidence_count = Column(Integer, default=0)
    source_count = Column(Integer, default=0)
    source_quality = Column(Float, default=0.0)  # 0..100
    reason = Column(Text, nullable=True)
    scored_by = Column(String, default="engine")  # "llm" or "engine"

    created_at = Column(DateTime, default=utcnow)

    leader = relationship("Leader", back_populates="scores")


class ScoreHistory(Base):
    """Versioned record so score changes over time are auditable/reproducible."""

    __tablename__ = "score_history"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=False)
    category = Column(String, index=True, nullable=False)
    score = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)
