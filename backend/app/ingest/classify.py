"""LLM-based evidence extraction/classification, grounded in real source text.

The model is only allowed to extract claims that are explicitly supported by the
provided document text (retrieval-augmented), and must map each to the fixed
category + evidence-classification taxonomy. It never invents facts or sources.
If no key is configured, ingestion cannot responsibly auto-tag real people, so
extraction is skipped.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

import httpx

from ..config import get_settings
from ..constants import CATEGORIES, EVIDENCE_TYPES
from .base import RawDoc

_CLASSIFICATIONS = list(EVIDENCE_TYPES.keys())

SYSTEM_PROMPT = f"""You extract structured transparency evidence from a source document.

STRICT RULES:
- Only extract claims EXPLICITLY SUPPORTED by the provided text. Never invent,
  infer beyond the text, or add outside knowledge. If nothing relevant, return [].
- You are NOT judging legal guilt; you are classifying documented public evidence.
- Each extracted item must map to exactly one CATEGORY from:
  {CATEGORIES}
- Each item must have a CLASSIFICATION from (choose the most accurate):
  {_CLASSIFICATIONS}
  Guidance: a conviction/ruling -> "COURT RECORD" or "VERIFIED FACT";
  charges/indictment/probe -> "ONGOING INVESTIGATION" or "COURT RECORD";
  wording like "alleged"/"accused" without adjudication -> "REPORTED ALLEGATION";
  official/government acts -> "OFFICIAL RECORD"/"POLICY DECISION";
  general press reporting -> "MEDIA REPORT"; contested items -> "DISPUTED CLAIM".
- POLARITY: -1 if the item reflects negatively on the leader for that category,
  +1 if positively, 0 if neutral/mixed.
- "claim": one concise sentence, paraphrased from the text (<= 240 chars).
- "date": "YYYY" or "YYYY-MM-DD" if the text states one, else null.

Return STRICT JSON only: {{"items": [{{"category","classification","polarity","claim","date"}}]}}
"""


@dataclass
class ExtractedEvidence:
    category: str
    classification: str
    polarity: int
    claim: str
    date: datetime | None


def _chunks(text: str, size: int = 6000, max_chunks: int = 8) -> list[str]:
    paras = text.split("\n")
    out, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 > size and cur:
            out.append(cur)
            cur = ""
            if len(out) >= max_chunks:
                break
        cur += p + "\n"
    if cur and len(out) < max_chunks:
        out.append(cur)
    return out


def _parse_date(s) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _call_llm(messages: list[dict]) -> dict:
    settings = get_settings()
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=60.0, verify=settings.verify_ssl) as client:
        r = client.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            json=payload, headers=headers,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def extract_evidence(leader_name: str, doc: RawDoc) -> list[ExtractedEvidence]:
    """Extract evidence items from a single document, grounded in its text."""
    settings = get_settings()
    if not settings.llm_enabled:
        return []

    cat_set = set(CATEGORIES)
    class_set = set(_CLASSIFICATIONS)
    results: list[ExtractedEvidence] = []
    seen: set[tuple] = set()

    chunks = _chunks(doc.text) if doc.kind == "document" else [doc.text[:6000]]
    for chunk in chunks:
        user = (
            f"Leader under review: {leader_name}\n"
            f"Source: {doc.source_name} ({doc.url})\n\n"
            f"DOCUMENT TEXT:\n{chunk}\n\n"
            "Extract the transparency evidence items now."
        )
        try:
            parsed = _call_llm(
                [{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": user}]
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[classify] chunk skipped: {type(exc).__name__}: {str(exc)[:80]}")
            continue

        for item in parsed.get("items", []):
            cat = str(item.get("category", "")).strip()
            cls = str(item.get("classification", "")).strip().upper()
            try:
                pol = int(item.get("polarity", 0))
            except (TypeError, ValueError):
                pol = 0
            claim = str(item.get("claim", "")).strip()
            if cat not in cat_set or cls not in class_set or pol not in (-1, 0, 1):
                continue
            if not claim:
                continue
            key = (cat, cls, pol, claim.lower()[:80])
            if key in seen:
                continue
            seen.add(key)
            results.append(
                ExtractedEvidence(
                    category=cat, classification=cls, polarity=pol, claim=claim,
                    date=_parse_date(item.get("date")) or doc.published_at,
                )
            )
    return results
