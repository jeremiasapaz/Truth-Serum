"""Real LLM scoring (OpenAI-compatible Chat Completions).

The LLM evaluates documented public evidence for a single (leader, category)
pair and returns a transparency score. It is explicitly instructed NOT to judge
legal guilt, to honour the controversial-topics policy, and to down-weight
single-source / disputed / unverified claims.

If no API key is configured, or the call fails / returns invalid JSON, we fall
back to the deterministic engine so the platform always produces a reproducible
result.
"""

from __future__ import annotations

import json
from collections.abc import Iterable

import httpx

from .config import get_settings
from .scoring import EvidenceInput, ScoreResult, compute_score

SYSTEM_PROMPT = """You are the scoring engine for a political transparency platform.

CORE PRINCIPLE: You do NOT determine legal guilt. You evaluate documented public
evidence and source weighting to assign a transparency score.

For each category you must return one of:
  +1 (positive)  0 (neutral)  -1 (negative)

Methodology you MUST follow:
- Prioritise VERIFIED FACT, OFFICIAL RECORD, COURT RECORD, GOVERNMENT DATA,
  NGO/INTERNATIONAL REPORTS, and multiple independent sources.
- Reduce the impact of single-source claims and purely political accusations.
- Apply LOWER confidence to DISPUTED CLAIM and UNVERIFIED CLAIM items.
- Explain uncertainty whenever evidence conflicts.
- Confidence (0-100) should reflect source quality, source quantity, recency,
  and evidence consistency.

Return STRICT JSON only, no prose, with this exact shape:
{"score": -1|0|1, "confidence": 0-100, "reason": "2-4 sentence justification"}
"""


def _format_evidence(evidence: Iterable[dict]) -> str:
    lines = []
    for i, e in enumerate(evidence, 1):
        lines.append(
            f"{i}. [{e['classification']}] polarity={e['polarity']:+d} "
            f"source={e['source_name']} (rating {e['source_rating']:.2f}) "
            f"date={e.get('published_at') or 'unknown'}\n"
            f"   title: {e['title']}\n"
            f"   text: {e.get('extracted_text') or '(none)'}"
        )
    return "\n".join(lines)


async def score_with_llm(
    *,
    leader_name: str,
    category: str,
    evidence_dicts: list[dict],
) -> ScoreResult:
    """Score using the LLM, falling back to the deterministic engine on any error."""
    settings = get_settings()

    # Deterministic result is always computed: it is the audit baseline and the
    # fallback, and we reuse its component breakdown regardless of who scored.
    det = compute_score(
        category,
        [
            EvidenceInput(
                classification=e["classification"],
                polarity=e["polarity"],
                source_name=e["source_name"],
                source_rating=e["source_rating"],
                published_at=e.get("published_at"),
            )
            for e in evidence_dicts
        ],
    )

    if not settings.llm_enabled or not evidence_dicts:
        det.reason = (det.reason or "") + (
            "" if settings.llm_enabled else " [Scored by deterministic engine: LLM key not set.]"
        )
        return det

    user_prompt = (
        f"Leader: {leader_name}\n"
        f"Category: {category}\n\n"
        f"Evidence records:\n{_format_evidence(evidence_dicts)}\n\n"
        "Assign the transparency score for this category now."
    )

    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=45.0, verify=settings.verify_ssl) as client:
            resp = await client.post(
                f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)

        score = int(parsed["score"])
        if score not in (-1, 0, 1):
            raise ValueError(f"invalid score {score}")
        confidence = float(parsed.get("confidence", det.confidence))
        confidence = max(0.0, min(confidence, 100.0))
        reason = str(parsed.get("reason", det.reason)).strip()

        # Keep the deterministic component breakdown + counts for auditability,
        # but use the LLM's score / confidence / reason.
        return ScoreResult(
            score=score,
            confidence=round(confidence, 1),
            evidence_count=det.evidence_count,
            source_count=det.source_count,
            source_quality=det.source_quality,
            components={**det.components, "llm_model": settings.llm_model},
            reason=reason,
        )
    except Exception as exc:  # noqa: BLE001 - any failure -> safe fallback
        det.reason = (det.reason or "") + f" [LLM scoring unavailable ({type(exc).__name__}); used deterministic engine.]"
        return det
