"""Administration summary: LLM narrative grounded in computed deltas, with a
deterministic templated fallback so a summary always exists."""

from __future__ import annotations

import json

import httpx

from ..config import get_settings


def _top_movers(analysis: dict, n: int = 6) -> list[dict]:
    inds = [i for i in analysis["indicators"] if i.get("delta") is not None]
    inds.sort(key=lambda i: abs(i["delta"]), reverse=True)
    return inds[:n]


def _facts(analysis: dict) -> dict:
    return {
        "leader": analysis["administration"]["leader_name"],
        "country": analysis["administration"]["country"],
        "citizen_reality_score": analysis["citizen_reality_score"],
        "leader_impact_score": analysis["leader_impact_score"],
        "green_energy_index": analysis["green_energy_index"],
        "category_scores": analysis["category_scores"],
        "shocks": analysis["shocks_during_office"],
        "top_movers": [
            {"name": i["name"], "unit": i["unit"], "baseline": i["baseline_mean"],
             "admin": i["admin_mean"], "delta_points": i["delta"], "pct_change": i["pct_change"]}
            for i in _top_movers(analysis)
        ],
    }


def templated_summary(analysis: dict) -> str:
    f = _facts(analysis)
    parts = [f"During {f['leader']}'s administration in {f['country']}:"]
    for m in f["top_movers"]:
        if m["baseline"] is None or m["admin"] is None:
            continue
        direction = "improved" if (m["delta_points"] or 0) >= 0 else "worsened"
        parts.append(
            f"- {m['name']} moved from {m['baseline']} to {m['admin']} {m['unit']} "
            f"({direction}, {m['pct_change']:+}%)."
        )
    crs = f["citizen_reality_score"]
    if crs.get("score") is not None:
        parts.append(f"- Citizen Reality Score: {crs.get('baseline')} -> {crs['score']} (/100).")
    gei = f["green_energy_index"]
    if gei.get("score") is not None:
        parts.append(f"- Green Energy Index: {gei['score']} /100 (delta {gei.get('delta')}).")
    parts.append(f"- Leader Impact Score: {f['leader_impact_score']['value']} (-100..+100).")
    if f["shocks"]:
        parts.append(f"- Global context during term: {', '.join(f['shocks'])}.")
    parts.append("Scores reflect documented indicators; administrative influence is "
                 "estimated, not a claim of direct causation.")
    return "\n".join(parts)


def generate_summary(analysis: dict) -> dict:
    settings = get_settings()
    facts = _facts(analysis)
    if not settings.llm_enabled:
        return {"summary": templated_summary(analysis), "generated_by": "template"}

    system = (
        "You write concise, neutral administration-performance summaries for a "
        "transparency platform. Use ONLY the provided numbers. Do not claim direct "
        "causation; say conditions improved/worsened, not that the leader caused it. "
        "Mention relevant global shocks as context. 4-7 sentences, specific numbers."
    )
    user = "Facts (JSON):\n" + json.dumps(facts, default=str)
    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=45.0, verify=settings.verify_ssl) as client:
            r = client.post(f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                            json=payload, headers=headers)
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"].strip()
        return {"summary": text, "generated_by": "llm"}
    except Exception as exc:  # noqa: BLE001
        return {"summary": templated_summary(analysis),
                "generated_by": f"template (llm failed: {type(exc).__name__})"}
