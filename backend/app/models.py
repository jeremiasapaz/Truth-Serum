from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
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
    return datetime.now(UTC)


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


# ===========================================================================
# Country Performance & Administration Impact Engine
# ===========================================================================
class Administration(Base):
    """A leader's term in office, used to measure country-condition changes."""

    __tablename__ = "administrations"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=True)
    leader_name = Column(String, index=True, nullable=False)
    country = Column(String, index=True, nullable=False)
    country_iso3 = Column(String, index=True, nullable=False)  # e.g. BRA, USA, GBR
    office = Column(String, nullable=True)
    party = Column(String, nullable=True)
    region = Column(String, index=True, nullable=True)
    continent = Column(String, index=True, nullable=True)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # null = still in office
    predecessor_name = Column(String, nullable=True)
    successor_name = Column(String, nullable=True)

    created_at = Column(DateTime, default=utcnow)


class IndicatorValue(Base):
    """A single (country, indicator, year) datapoint with full source traceability.

    No calculated score may exist without one of these underneath it.
    """

    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True, index=True)
    country_iso3 = Column(String, index=True, nullable=False)
    indicator_code = Column(String, index=True, nullable=False)
    year = Column(Integer, index=True, nullable=False)
    value = Column(Float, nullable=True)

    dataset_name = Column(String, nullable=True)
    source_name = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    collected_at = Column(DateTime, default=utcnow)


# ===========================================================================
# Financial Transparency
# ===========================================================================
class FinancialData(Base):
    """Financial data for leaders: salary, assets, wealth, income sources."""

    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=False)
    
    # Salary and public income
    annual_salary = Column(Float, nullable=True)  # Annual salary in USD
    public_benefits = Column(Float, nullable=True)  # Benefits, allowances, etc.
    year = Column(Integer, index=True, nullable=True)  # Year of data
    
    # Assets and wealth
    total_assets = Column(Float, nullable=True)  # Total assets in USD
    real_estate = Column(Float, nullable=True)  # Real estate value
    investments = Column(Float, nullable=True)  # Investment portfolio
    cash = Column(Float, nullable=True)  # Cash and bank accounts
    other_assets = Column(Float, nullable=True)  # Other assets
    
    # Debt
    total_debt = Column(Float, nullable=True)  # Total debt/liabilities
    net_worth = Column(Float, nullable=True)  # Net worth (assets - debt)
    
    # Income sources breakdown
    public_income = Column(Float, nullable=True)  # Income from public office
    private_income = Column(Float, nullable=True)  # Income from private sources
    investment_income = Column(Float, nullable=True)  # Income from investments
    other_income = Column(Float, nullable=True)  # Other income sources
    
    # Verification
    source = Column(String, nullable=True)  # Source of financial data
    source_url = Column(String, nullable=True)
    verified = Column(Integer, default=0)  # 0 = unverified, 1 = verified
    notes = Column(Text, nullable=True)  # Additional context
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    leader = relationship("Leader")


# ===========================================================================
# Speech Transcripts
# ===========================================================================
class SpeechTranscript(Base):
    """Transcript of a political speech or public statement from video platforms."""

    __tablename__ = "speech_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    leader_id = Column(Integer, ForeignKey("leaders.id"), nullable=False)
    
    # Video/platform metadata
    platform = Column(String, index=True, nullable=False)  # youtube, tiktok, etc.
    video_url = Column(String, nullable=False, index=True)
    video_id = Column(String, index=True)  # YouTube video ID, TikTok ID, etc.
    
    # Speech metadata
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    event = Column(String, nullable=True)  # e.g., "Campaign rally", "Press conference"
    
    # Transcript
    transcript_text = Column(Text, nullable=False)
    language = Column(String, default="en")  # en, pt, etc.
    
    # Classification (LLM analysis)
    offense_categories = Column(String, nullable=True)  # e.g., "racist,homophobic"
    flagged_quotes = Column(Text, nullable=True)  # JSON array of problematic quotes
    classification_confidence = Column(Float, default=0.0)
    classified_by = Column(String, default="manual")  # manual, llm
    
    # Submission metadata
    submitted_by = Column(String, nullable=True)  # user who submitted
    submitted_at = Column(DateTime, default=utcnow)
    verified = Column(Integer, default=0)  # 0 = unverified, 1 = verified
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    leader = relationship("Leader")
