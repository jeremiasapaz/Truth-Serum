"""Deterministic Trust & Confidence engine.

Every category score is reproducible from the stored evidence. The LLM layer
(see llm.py) may enrich the human-readable justification, but the numeric score,
confidence and component breakdown are always computable here so results stay
auditable and reproducible.

Final confidence is composed of:
    40% Source Quality
    25% Source Quantity
    20% Recency
    15% Evidence Consistency
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from .constants import (
    CONTROVERSIAL_CATEGORIES,
    DEFAULT_EVIDENCE_WEIGHT,
    EVIDENCE_TYPES,
    TRUST_WEIGHTS,
)


@dataclass
class EvidenceInput:
    classification: str
    polarity: int  # -1, 0, +1
    source_name: str
    source_rating: float  # 0..1
    published_at: datetime | None = None


@dataclass
class ScoreResult:
    score: int                 # -1 / 0 / +1
    confidence: float          # 0..100
    evidence_count: int
    source_count: int
    source_quality: float      # 0..100
    components: dict = field(default_factory=dict)
    reason: str = ""


def _evidence_weight(classification: str) -> float:
    return EVIDENCE_TYPES.get(classification.upper(), DEFAULT_EVIDENCE_WEIGHT)


def _recency_factor(published_at: datetime | None, half_life_days: float = 1825.0) -> float:
    """Exponential decay. Evidence ~5 years old counts roughly half.

    Undated evidence gets a neutral-ish 0.5 so it neither dominates nor vanishes.
    """
    if published_at is None:
        return 0.5
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - published_at).days
    age_days = max(age_days, 0)
    return math.exp(-math.log(2) * age_days / half_life_days)


def _saturating(n: float, k: float) -> float:
    """Map a count to 0..1 with diminishing returns (saturates near 1)."""
    return 1.0 - math.exp(-n / k)


def compute_score(category: str, evidence: Iterable[EvidenceInput]) -> ScoreResult:
    evidence = list(evidence)
    if not evidence:
        return ScoreResult(
            score=0,
            confidence=0.0,
            evidence_count=0,
            source_count=0,
            source_quality=0.0,
            components={"source_quality": 0, "source_quantity": 0, "recency": 0, "consistency": 0},
            reason="No documented public evidence available for this category.",
        )

    controversial = category in CONTROVERSIAL_CATEGORIES
    distinct_sources = {e.source_name for e in evidence}

    weighted_polarity = 0.0
    total_weight = 0.0
    quality_num = 0.0
    quality_den = 0.0
    recency_num = 0.0
    recency_den = 0.0

    for e in evidence:
        w = _evidence_weight(e.classification)
        # Controversial topics: discount low-reliability classifications further
        # so single disputed/unverified claims cannot drive the score.
        if controversial and w < 0.5:
            w *= 0.5

        combined = w * max(e.source_rating, 0.0)
        weighted_polarity += e.polarity * combined
        total_weight += combined

        quality_num += e.source_rating * w
        quality_den += w

        rf = _recency_factor(e.published_at)
        recency_num += rf * w
        recency_den += w

    # --- Component 1: Source Quality (0..1) ---
    source_quality = quality_num / quality_den if quality_den else 0.0

    # --- Component 2: Source Quantity (0..1) ---
    # Rewards both many evidence records AND multiple independent sources.
    ev_factor = _saturating(len(evidence), k=5.0)
    src_factor = _saturating(len(distinct_sources), k=3.0)
    source_quantity = 0.5 * ev_factor + 0.5 * src_factor

    # --- Component 3: Recency (0..1) ---
    recency = recency_num / recency_den if recency_den else 0.5

    # --- Component 4: Consistency (0..1) ---
    # How strongly the weighted evidence agrees on a direction.
    if total_weight > 0:
        consistency = abs(weighted_polarity) / total_weight
    else:
        consistency = 0.0

    confidence = (
        TRUST_WEIGHTS["source_quality"] * source_quality
        + TRUST_WEIGHTS["source_quantity"] * source_quantity
        + TRUST_WEIGHTS["recency"] * recency
        + TRUST_WEIGHTS["consistency"] * consistency
    ) * 100.0

    # Single-source controversial claims get a confidence penalty.
    if controversial and len(distinct_sources) < 2:
        confidence *= 0.6

    # --- Final direction: -1 / 0 / +1 ---
    net = weighted_polarity / total_weight if total_weight else 0.0
    threshold = 0.20 if controversial else 0.12
    if net <= -threshold:
        score = -1
    elif net >= threshold:
        score = 1
    else:
        score = 0

    components = {
        "source_quality": round(source_quality * 100, 1),
        "source_quantity": round(source_quantity * 100, 1),
        "recency": round(recency * 100, 1),
        "consistency": round(consistency * 100, 1),
        "net_polarity": round(net, 3),
    }

    reason = _auto_reason(category, score, evidence, distinct_sources, net)

    return ScoreResult(
        score=score,
        confidence=round(min(confidence, 100.0), 1),
        evidence_count=len(evidence),
        source_count=len(distinct_sources),
        source_quality=round(source_quality * 100, 1),
        components=components,
        reason=reason,
    )


def _auto_reason(category, score, evidence, sources, net) -> str:
    source_list = ", ".join(sorted(sources))
    direction = {
        -1: "the available evidence points to significant concerns",
        0: "evidence is mixed, limited, or inconclusive",
        1: "the available evidence is predominantly favourable",
    }[score]
    strong = sorted(
        {e.classification for e in evidence if _evidence_weight(e.classification) >= 0.75}
    )
    strong_note = (
        f" High-reliability evidence present: {', '.join(strong)}."
        if strong
        else " No high-reliability (court/official/verified) evidence present."
    )
    return (
        f"For {category}, {direction} (net polarity {net:+.2f}). "
        f"Based on {len(evidence)} evidence record(s) across {len(sources)} "
        f"source(s): {source_list}.{strong_note} "
        "Score reflects documented public evidence and source weighting, not legal guilt."
    )
