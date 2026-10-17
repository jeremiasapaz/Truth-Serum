"""Eurostat collector (free, no key) — JSON-stat format.

Covers EU/EEA countries (plus UK historical). For this platform that means
Ireland and the UK; non-European countries are skipped. Used for housing /
cost-of-living series the World Bank does not provide.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..ingest.base import http_client

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# ISO3 -> Eurostat geo code (Eurostat uses 2-letter, 'UK' not 'GB', 'EL' for Greece).
ISO3_TO_EUROSTAT = {
    "IRL": "IE", "GBR": "UK", "DEU": "DE", "FRA": "FR", "ESP": "ES", "ITA": "IT",
    "PRT": "PT", "NLD": "NL", "SWE": "SE", "POL": "PL", "BEL": "BE", "AUT": "AT",
    "DNK": "DK", "FIN": "FI", "GRC": "EL", "CZE": "CZ", "HUN": "HU", "ROU": "RO",
}


@dataclass
class EurostatSeries:
    dataset: str
    indicator_name: str
    source_name: str
    source_url: str
    api_url: str
    values: dict[int, float]


def _strides(sizes: list[int]) -> list[int]:
    strides = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]
    return strides


def fetch_series(iso3: str, dataset: str, dim_choices: dict | None = None) -> EurostatSeries | None:
    geo = ISO3_TO_EUROSTAT.get(iso3.upper())
    if not geo:
        return None  # not an EU/EEA country
    api_url = f"{BASE}/{dataset}?format=JSON&geo={geo}"
    try:
        with http_client(timeout=30.0) as client:
            r = client.get(api_url)
            r.raise_for_status()
            d = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[eurostat] {iso3} {dataset} skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return None

    ids = d.get("id", [])
    sizes = d.get("size", [])
    dims = d.get("dimension", {})
    if "time" not in ids or "geo" not in ids or not sizes:
        return None
    strides = _strides(sizes)
    dim_choices = dim_choices or {}

    # Fixed position for each non-time dimension.
    fixed = {}
    for name in ids:
        if name == "time":
            continue
        cat = dims[name]["category"]["index"]
        if name == "geo":
            if geo not in cat:
                return None
            fixed[name] = cat[geo]
        elif name in dim_choices and dim_choices[name] in cat:
            fixed[name] = cat[dim_choices[name]]
        else:
            fixed[name] = 0  # first member (defaults to TOTAL / base-year index)

    time_cat = dims["time"]["category"]["index"]  # code -> pos
    values_raw = d.get("value", {})

    def get_val(linear):
        if isinstance(values_raw, list):
            return values_raw[linear] if 0 <= linear < len(values_raw) else None
        return values_raw.get(str(linear))

    out: dict[int, float] = {}
    for code, pos in time_cat.items():
        linear = sum(
            (pos if name == "time" else fixed[name]) * strides[i]
            for i, name in enumerate(ids)
        )
        v = get_val(linear)
        if v is None:
            continue
        try:
            out[int(code)] = float(v)
        except (TypeError, ValueError):
            continue

    if not out:
        return None
    name = d.get("label", dataset)
    return EurostatSeries(
        dataset=dataset, indicator_name=name, source_name="Eurostat",
        source_url=f"https://ec.europa.eu/eurostat/databrowser/view/{dataset}/default/table?lang=en",
        api_url=api_url, values=out,
    )
