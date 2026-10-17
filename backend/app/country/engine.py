"""Period analysis + scoring for the Country Performance engine.

All composites are reproducible from stored IndicatorValue rows:

- Each indicator value is normalized 0-100 against the country's own historical
  range for that series (direction-adjusted), so higher is always better.
- Category Score = mean of its indicators' administration-period normalized scores.
- Deltas compare the administration period to the 3-year baseline before office.
- Citizen Reality Score (0-100) = weighted mean of citizen-facing category scores.
- Green Energy Index (0-100) = mean of green-energy indicators.
- Leader Impact Score (-100..+100) blends "vs inherited" and "left behind"
  trends, dampened during overlapping global shocks (documented, never a claim
  of direct causation).
"""

from __future__ import annotations

from datetime import datetime
from statistics import mean

from sqlalchemy.orm import Session

from .. import models
from .catalog import (
    CRS_WEIGHTS,
    GEI_CODES,
    PERFORMANCE_CATEGORIES,
    QOL_CATEGORIES,
    SUSTAINABILITY_INDICES,
    by_code,
    wb_indicators,
)

# Major global shocks (year -> label) used to contextualize, not excuse.
GLOBAL_SHOCKS = {
    2008: "Global Financial Crisis", 2009: "Global Financial Crisis",
    2020: "COVID-19 pandemic", 2021: "COVID-19 pandemic",
    2022: "Energy/inflation shock (Russia-Ukraine war)",
}


def _year(d: datetime | None) -> int | None:
    return d.year if d else None


def compute_periods(admin: models.Administration) -> dict[str, dict]:
    start = admin.start_date.year
    end = _year(admin.end_date)
    cur = datetime.utcnow().year
    admin_end = end if end else cur
    periods = {
        "baseline": {"start": start - 3, "end": start - 1, "label": "3 years before office"},
        "campaign": {"start": start - 1, "end": start, "label": "Election/campaign period"},
        "administration": {"start": start, "end": admin_end, "label": "Time in office"},
    }
    if end:
        periods["transition"] = {"start": end + 1, "end": end + 1, "label": "First year after office"}
        periods["successor"] = {"start": end + 1, "end": end + 2, "label": "Successor first 2 years"}
    return periods


def _period_mean(values: dict[int, float], lo: int, hi: int) -> float | None:
    pts = [v for y, v in values.items() if lo <= y <= hi]
    return mean(pts) if pts else None


def _normalize(value: float | None, values: dict[int, float], direction: str) -> float | None:
    """Map a value to 0-100 vs the country's own historical range (direction-adjusted)."""
    if value is None or not values:
        return None
    lo, hi = min(values.values()), max(values.values())
    if hi == lo:
        return 50.0
    frac = (value - lo) / (hi - lo)
    if direction == "lower_better":
        frac = 1.0 - frac
    return round(max(0.0, min(1.0, frac)) * 100, 1)


def _load_series(db: Session, iso3: str) -> dict[str, dict[int, float]]:
    rows = (
        db.query(models.IndicatorValue)
        .filter(models.IndicatorValue.country_iso3 == iso3)
        .all()
    )
    out: dict[str, dict[int, float]] = {}
    meta: dict[str, models.IndicatorValue] = {}
    for r in rows:
        if r.value is None:
            continue
        out.setdefault(r.indicator_code, {})[r.year] = r.value
        meta[r.indicator_code] = r
    out["__meta__"] = meta  # type: ignore
    return out


def analyze_administration(db: Session, admin: models.Administration) -> dict:
    periods = compute_periods(admin)
    series_map = _load_series(db, admin.country_iso3)
    meta = series_map.pop("__meta__", {})  # type: ignore
    catalog = by_code()

    base = periods["baseline"]
    adm = periods["administration"]

    indicator_results = []
    cat_admin: dict[str, list[float]] = {}
    cat_delta: dict[str, list[float]] = {}

    for ind in wb_indicators():
        series = ind.code.split("|")[0]
        values = series_map.get(series)
        if not values:
            continue
        admin_mean = _period_mean(values, adm["start"], adm["end"])
        base_mean = _period_mean(values, base["start"], base["end"])
        admin_score = _normalize(admin_mean, values, ind.direction)
        base_score = _normalize(base_mean, values, ind.direction)
        if admin_score is None:
            continue

        delta = round(admin_score - base_score, 1) if base_score is not None else None
        pct = None
        if base_mean not in (None, 0) and admin_mean is not None:
            raw = (admin_mean - base_mean) / abs(base_mean) * 100
            pct = round(raw if ind.direction == "higher_better" else -raw, 1)

        m = meta.get(series)
        indicator_results.append({
            "code": ind.code, "name": ind.name, "category": ind.category,
            "unit": ind.unit, "direction": ind.direction, "dataset": ind.dataset,
            "source_name": getattr(m, "source_name", "World Bank"),
            "source_url": getattr(m, "source_url", ""),
            "admin_mean": round(admin_mean, 2) if admin_mean is not None else None,
            "baseline_mean": round(base_mean, 2) if base_mean is not None else None,
            "admin_score": admin_score, "baseline_score": base_score,
            "delta": delta, "pct_change": pct,
            "history": dict(sorted(values.items())),
        })
        cat_admin.setdefault(ind.category, []).append(admin_score)
        if delta is not None:
            cat_delta.setdefault(ind.category, []).append(delta)

    def cat_block(cats):
        out = {}
        for c in cats:
            if c in cat_admin:
                out[c] = {
                    "score": round(mean(cat_admin[c]), 1),
                    "delta": round(mean(cat_delta[c]), 1) if cat_delta.get(c) else None,
                    "indicator_count": len(cat_admin[c]),
                }
        return out

    category_scores = cat_block(PERFORMANCE_CATEGORIES)
    qol_scores = cat_block(QOL_CATEGORIES + ["Health", "Security"])

    # Green Energy Index
    gei_scores = [r["admin_score"] for r in indicator_results if r["code"] in GEI_CODES]
    gei_deltas = [r["delta"] for r in indicator_results if r["code"] in GEI_CODES and r["delta"] is not None]
    green_energy_index = {
        "score": round(mean(gei_scores), 1) if gei_scores else None,
        "delta": round(mean(gei_deltas), 1) if gei_deltas else None,
    }

    # Sustainability sub-indices
    score_by_code = {r["code"]: r["admin_score"] for r in indicator_results}
    sustainability = {}
    for name, codes in SUSTAINABILITY_INDICES.items():
        vals = [score_by_code[c] for c in codes if c in score_by_code]
        if vals:
            sustainability[name] = round(mean(vals), 1)

    # Citizen Reality Score (weighted, renormalized by available weight)
    crs_num, crs_w = 0.0, 0.0
    crs_base_num = 0.0
    all_cat = {**category_scores, **qol_scores}
    for cat, w in CRS_WEIGHTS.items():
        if cat in all_cat:
            crs_num += all_cat[cat]["score"] * w
            crs_w += w
            if all_cat[cat]["delta"] is not None:
                crs_base_num += (all_cat[cat]["score"] - all_cat[cat]["delta"]) * w
    crs = round(crs_num / crs_w, 1) if crs_w else None
    crs_base = round(crs_base_num / crs_w, 1) if crs_w else None
    citizen_reality_score = {
        "score": crs, "baseline": crs_base,
        "delta": round(crs - crs_base, 1) if (crs is not None and crs_base is not None) else None,
    }

    # Leader Impact Score (-100..+100) with documented shock dampening
    shocks = sorted({GLOBAL_SHOCKS[y] for y in range(adm["start"], adm["end"] + 1) if y in GLOBAL_SHOCKS})
    all_deltas = [r["delta"] for r in indicator_results if r["delta"] is not None]
    econ_deltas = [r["delta"] for r in indicator_results
                   if r["category"] == "Economy" and r["delta"] is not None]
    vs_inherited = mean(all_deltas) if all_deltas else 0.0
    # "Left behind": within-office end-vs-start trend
    left_vals = []
    for r in indicator_results:
        hist = r["history"]
        yrs = [y for y in hist if adm["start"] <= y <= adm["end"]]
        if len(yrs) >= 2:
            ind = catalog[r["code"]]
            s = _normalize(hist[min(yrs)], dict(hist), ind.direction)
            e = _normalize(hist[max(yrs)], dict(hist), ind.direction)
            if s is not None and e is not None:
                left_vals.append(e - s)
    left_behind = mean(left_vals) if left_vals else 0.0
    lis_raw = 0.6 * vs_inherited + 0.4 * left_behind
    if shocks and econ_deltas and mean(econ_deltas) < 0:
        lis_raw += abs(mean(econ_deltas)) * 0.25 * (len([r for r in indicator_results if r["category"] == "Economy"]) / max(len(all_deltas), 1))
    leader_impact_score = {
        "value": round(max(-100.0, min(100.0, lis_raw * 2.2)), 1),
        "vs_inherited": round(vs_inherited, 1),
        "left_behind": round(left_behind, 1),
        "shocks": shocks,
        "note": "Estimated administrative influence, not a claim of direct causation.",
    }

    total_wb = len(wb_indicators())
    coverage_n = len(indicator_results)
    confidence = round(min(100.0, coverage_n / total_wb * 100) * 0.95, 1)

    return {
        "administration": {
            "id": admin.id, "leader_name": admin.leader_name, "country": admin.country,
            "country_iso3": admin.country_iso3, "office": admin.office, "party": admin.party,
            "start": admin.start_date.date().isoformat(),
            "end": admin.end_date.date().isoformat() if admin.end_date else None,
            "predecessor": admin.predecessor_name, "successor": admin.successor_name,
        },
        "periods": periods,
        "indicators": indicator_results,
        "category_scores": category_scores,
        "qol_scores": qol_scores,
        "green_energy_index": green_energy_index,
        "sustainability": sustainability,
        "citizen_reality_score": citizen_reality_score,
        "leader_impact_score": leader_impact_score,
        "confidence": confidence,
        "coverage": {"available": coverage_n, "total": total_wb},
        "shocks_during_office": shocks,
    }
