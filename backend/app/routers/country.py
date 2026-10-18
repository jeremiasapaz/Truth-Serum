import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models
from ..country.catalog import (
    INDICATORS,
    PERFORMANCE_CATEGORIES,
    QOL_CATEGORIES,
    SUSTAINABILITY_INDICES,
)
from ..country.engine import analyze_administration, benchmark_administration
from ..country.ingest import ingest_country
from ..country.summary import generate_summary
from ..database import get_db

router = APIRouter(prefix="/api/country", tags=["country"])


def _compact(analysis: dict) -> dict:
    a = analysis["administration"]
    return {
        **a,
        "citizen_reality_score": analysis["citizen_reality_score"]["score"],
        "citizen_reality_delta": analysis["citizen_reality_score"].get("delta"),
        "leader_impact_score": analysis["leader_impact_score"]["value"],
        "green_energy_index": analysis["green_energy_index"]["score"],
        "green_energy_delta": analysis["green_energy_index"].get("delta"),
        "confidence": analysis["confidence"],
        "coverage": analysis["coverage"],
        "category_scores": {c: v["score"] for c, v in analysis["category_scores"].items()},
        "has_data": analysis["coverage"]["available"] > 0,
    }


SORTS = {
    "name", "leader_impact_desc", "citizen_reality_desc",
    "best_economy", "best_health", "best_education", "best_security",
    "best_housing", "best_cost_of_living", "best_green_energy",
    "most_improved", "most_declined",
}


@router.get("/administrations")
def list_administrations(
    db: Session = Depends(get_db),
    country: str | None = None,
    continent: str | None = None,
    sort: str = "name",
):
    q = db.query(models.Administration)
    if country:
        q = q.filter(models.Administration.country == country)
    if continent:
        q = q.filter(models.Administration.continent == continent)
    admins = q.all()
    items = [_compact(analyze_administration(db, a)) for a in admins]

    def cat(i, c):
        return i["category_scores"].get(c, -1)

    keymap = {
        "name": lambda i: i["leader_name"].lower(),
        "leader_impact_desc": lambda i: -(i["leader_impact_score"] or -999),
        "citizen_reality_desc": lambda i: -(i["citizen_reality_score"] or -1),
        "best_economy": lambda i: -cat(i, "Economy"),
        "best_health": lambda i: -cat(i, "Health"),
        "best_education": lambda i: -cat(i, "Education"),
        "best_security": lambda i: -cat(i, "Security"),
        "best_housing": lambda i: -cat(i, "Housing"),
        "best_cost_of_living": lambda i: -cat(i, "Cost of Living"),
        "best_green_energy": lambda i: -(i["green_energy_index"] or -1),
        "most_improved": lambda i: -(i["leader_impact_score"] or -999),
        "most_declined": lambda i: (i["leader_impact_score"] or 999),
    }
    if sort not in keymap:
        sort = "name"
    items.sort(key=keymap[sort])
    return items


@router.get("/filters/options")
def filter_options(db: Session = Depends(get_db)):
    countries = sorted({a.country for a in db.query(models.Administration).all()})
    continents = sorted({a.continent for a in db.query(models.Administration).all() if a.continent})
    return {"countries": countries, "continents": continents, "sorts": sorted(SORTS)}


@router.get("/indicators")
def indicators_catalog():
    return {
        "performance_categories": PERFORMANCE_CATEGORIES,
        "qol_categories": QOL_CATEGORIES,
        "sustainability_indices": list(SUSTAINABILITY_INDICES),
        "normalization": "0-100 vs the country's own historical range, direction-adjusted.",
        "indicators": [
            {
                "code": i.code, "name": i.name, "category": i.category, "unit": i.unit,
                "direction": i.direction,
                "source": i.source or "pluggable",
                "dataset": i.dataset, "pluggable_source": i.pluggable_source,
                "live": i.source is not None,
            }
            for i in INDICATORS
        ],
    }


@router.get("/administration/{admin_id}")
def administration_detail(admin_id: int, db: Session = Depends(get_db)):
    admin = db.get(models.Administration, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administration not found")
    return analyze_administration(db, admin)


@router.get("/administration/{admin_id}/summary")
def administration_summary(admin_id: int, db: Session = Depends(get_db)):
    admin = db.get(models.Administration, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administration not found")
    analysis = analyze_administration(db, admin)
    if not analysis["indicators"]:
        return {"summary": "No indicator data ingested yet for this country. "
                "Run ingestion first.", "generated_by": "none"}
    return generate_summary(analysis)


@router.get("/administration/{admin_id}/benchmark")
def administration_benchmark(admin_id: int, db: Session = Depends(get_db)):
    admin = db.get(models.Administration, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administration not found")
    return benchmark_administration(db, admin)


@router.get("/compare")
def compare(ids: list[int] = Query(...), db: Session = Depends(get_db)):
    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Compare at most 10 administrations")
    out = []
    for i in ids:
        a = db.get(models.Administration, i)
        if a:
            out.append(analyze_administration(db, a))
    return {"administrations": out}


@router.post("/ingest/{admin_id}")
def ingest_for_admin(admin_id: int, start_year: int = 2000, db: Session = Depends(get_db)):
    admin = db.get(models.Administration, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administration not found")
    return ingest_country(db, admin.country_iso3, start_year=start_year)


@router.post("/ingest-country/{iso3}")
def ingest_for_country(iso3: str, start_year: int = 2000, db: Session = Depends(get_db)):
    return ingest_country(db, iso3, start_year=start_year)


@router.get("/administration/{admin_id}/export.csv")
def export_csv(admin_id: int, db: Session = Depends(get_db)):
    admin = db.get(models.Administration, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Administration not found")
    rows = (
        db.query(models.IndicatorValue)
        .filter(models.IndicatorValue.country_iso3 == admin.country_iso3)
        .order_by(models.IndicatorValue.indicator_code, models.IndicatorValue.year)
        .all()
    )
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["country_iso3", "indicator_code", "dataset", "year", "value",
                "source_name", "source_url"])
    for r in rows:
        w.writerow([r.country_iso3, r.indicator_code, r.dataset_name, r.year,
                    r.value, r.source_name, r.source_url])
    buf.seek(0)
    fname = f"{admin.country_iso3}_{admin.leader_name.replace(' ', '_')}_indicators.csv"
    return StreamingResponse(
        iter([buf.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )
