"""Fetch World Bank series for a country and store them as IndicatorValue rows."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from .. import models
from .catalog import owid_indicators, wb_series_codes
from .owid import fetch_series as fetch_owid
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

    # OWID series (green energy capacity, V-Dem democracy, wellbeing, ...)
    for ind in owid_indicators():
        ow = fetch_owid(iso3, ind.provider_code, ind.col_index)
        if ow is None or not ow.values:
            continue
        series_ok += 1
        db.query(models.IndicatorValue).filter(
            models.IndicatorValue.country_iso3 == iso3,
            models.IndicatorValue.indicator_code == ind.code,
        ).delete()
        for year, value in ow.values.items():
            if year < start_year or year > end_year:
                continue
            db.add(models.IndicatorValue(
                country_iso3=iso3, indicator_code=ind.code, year=year, value=value,
                dataset_name=f"{ind.name} ({ow.indicator_name})",
                source_name=ow.source_name, source_url=ow.source_url,
            ))
            added += 1
    db.commit()
    total = len(wb_series_codes()) + len(owid_indicators())
    return {"country_iso3": iso3, "series_fetched": series_ok,
            "series_total": total, "values_added": added,
            "range": [start_year, end_year]}
