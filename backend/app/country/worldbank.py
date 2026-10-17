"""World Bank Open Data collector (free, no key).

Returns full historical time series with the metadata needed for auditability:
the dataset/indicator name, the exact API query URL (traceable + downloadable),
and the provider name.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..ingest.base import http_client

BASE = "https://api.worldbank.org/v2"


@dataclass
class WBSeries:
    series_code: str
    indicator_name: str
    source_name: str
    source_url: str          # human/data page
    api_url: str             # machine-readable (downloadable JSON)
    values: dict[int, float]  # year -> value (only non-null)


def fetch_series(iso3: str, series_code: str, start: int, end: int) -> WBSeries | None:
    api_url = (
        f"{BASE}/country/{iso3}/indicator/{series_code}"
        f"?format=json&date={start}:{end}&per_page=500"
    )
    try:
        with http_client(timeout=25.0) as client:
            r = client.get(api_url)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[worldbank] {iso3} {series_code} skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return None

    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None

    rows = data[1]
    name = rows[0].get("indicator", {}).get("value", series_code)
    values: dict[int, float] = {}
    for row in rows:
        v = row.get("value")
        try:
            year = int(row.get("date"))
        except (TypeError, ValueError):
            continue
        if v is not None:
            values[year] = float(v)

    data_page = f"https://data.worldbank.org/indicator/{series_code}?locations={iso3}"
    return WBSeries(
        series_code=series_code,
        indicator_name=name,
        source_name="World Bank",
        source_url=data_page,
        api_url=api_url,
        values=values,
    )
