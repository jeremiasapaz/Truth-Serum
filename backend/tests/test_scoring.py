"""Smoke + behaviour tests for the deterministic scoring engine."""

from datetime import UTC, datetime

from app.scoring import EvidenceInput, compute_score


def _ev(classification, polarity, source, rating, days_ago=30):
    return EvidenceInput(
        classification=classification,
        polarity=polarity,
        source_name=source,
        source_rating=rating,
        published_at=datetime.now(UTC).replace(microsecond=0),
    )


def test_empty_evidence_is_neutral_zero_confidence():
    r = compute_score("Corruption", [])
    assert r.score == 0
    assert r.confidence == 0.0
    assert r.evidence_count == 0


def test_strong_negative_evidence_yields_negative_score():
    ev = [
        _ev("COURT RECORD", -1, "Court Records", 0.98),
        _ev("INTERNATIONAL REPORT", -1, "Transparency International", 0.92),
        _ev("MEDIA REPORT", -1, "Reuters", 0.90),
    ]
    r = compute_score("Corruption", ev)
    assert r.score == -1
    assert r.source_count == 3
    assert r.confidence > 0


def test_strong_positive_evidence_yields_positive_score():
    ev = [
        _ev("OFFICIAL RECORD", 1, "Official Gazette", 0.95),
        _ev("INTERNATIONAL REPORT", 1, "OECD", 0.90),
    ]
    r = compute_score("Democratic Integrity", ev)
    assert r.score == 1


def test_single_unverified_claim_is_discounted_on_controversial():
    ev = [_ev("UNVERIFIED CLAIM", -1, "Anonymous Blog", 0.15)]
    r = compute_score("Scandals", ev)
    # Single low-reliability source on a controversial topic -> low confidence.
    assert r.confidence < 40


def test_confidence_components_present():
    ev = [_ev("COURT RECORD", -1, "Court Records", 0.98)]
    r = compute_score("Crime", ev)
    for key in ("source_quality", "source_quantity", "recency", "consistency"):
        assert key in r.components
