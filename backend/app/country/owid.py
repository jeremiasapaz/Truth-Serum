"""Our World in Data (OWID) collector (free, no key).

Fetches a grapher dataset as CSV (Entity, Code, Year, <value>, ...) and returns
a per-year series for one country, with dataset name + source URL for auditability.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from ..ingest.base import http_client


@dataclass
class OWIDSeries:
    slug: str
    indicator_name: str
    source_name: str
    source_url: str
    api_url: str
    values: dict[int, float]


def fetch_series(iso3: str, slug: str, col_index: int = 3) -> OWIDSeries | None:
    api_url = f"https://ourworldindata.org/grapher/{slug}.csv?country=~{iso3}"
    try:
        with http_client(timeout=25.0) as client:
            r = client.get(api_url)
            r.raise_for_status()
            text = r.text
    except Exception as exc:  # noqa: BLE001
        print(f"[owid] {iso3} {slug} skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return None

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if len(rows) < 2:
        return None
    header = rows[0]
    if col_index >= len(header):
        col_index = 3 if len(header) > 3 else len(header) - 1
    value_name = header[col_index] if col_index < len(header) else slug

    values: dict[int, float] = {}
    for row in rows[1:]:
        if len(row) <= max(col_index, 2):
            continue
        if row[1].strip().upper() != iso3.upper():
            continue
        try:
            year = int(row[2])
            values[year] = float(row[col_index])
        except (TypeError, ValueError):
            continue

    if not values:
        return None
    return OWIDSeries(
        slug=slug, indicator_name=value_name, source_name="Our World in Data",
        source_url=f"https://ourworldindata.org/grapher/{slug}",
        api_url=api_url, values=values,
    )
