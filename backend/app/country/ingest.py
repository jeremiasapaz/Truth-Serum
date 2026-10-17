"""Fetch World Bank series for a country and store them as IndicatorValue rows."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from .. import models
from .catalog import wb_series_codes
from .worldbank import fetch_series


def ingest_country(db: Session, iso3: str, start_year: int = 2000,
                   end_year: int | None = None) -> dict:
    end_year = end_year or datetime.now(UTC).year
    iso3 = iso3.upper()

    added, series_ok = 0, 0
    for series in wb_series_codes():
        wb = fetch_series(iso3, series, start_year, end_year)
        if wb is None or not wb.values:
            continue
        series_ok += 1
        # Replace existing rows for this country+series (reproducible re-runs).
        db.query(models.IndicatorValue).filter(
            models.IndicatorValue.country_iso3 == iso3,
            models.IndicatorValue.indicator_code == series,
        ).delete()
        for year, value in wb.values.items():
            db.add(models.IndicatorValue(
                country_iso3=iso3, indicator_code=series, year=year, value=value,
                dataset_name=wb.indicator_name, source_name=wb.source_name,
                source_url=wb.source_url,
            ))
            added += 1
    db.commit()
    return {"country_iso3": iso3, "series_fetched": series_ok,
            "series_total": len(wb_series_codes()), "values_added": added,
            "range": [start_year, end_year]}
