"""Tests for the Country Performance engine (period math + normalization)."""

from datetime import datetime

from app.country.engine import _normalize, compute_periods
from app.models import Administration


def test_compute_periods_in_office():
    admin = Administration(
        leader_name="X", country="Brazil", country_iso3="BRA",
        start_date=datetime(2019, 1, 1), end_date=datetime(2022, 12, 31),
    )
    p = compute_periods(admin)
    assert p["baseline"] == {"start": 2016, "end": 2018, "label": "3 years before office"}
    assert p["administration"]["start"] == 2019 and p["administration"]["end"] == 2022
    assert p["transition"]["start"] == 2023
    assert p["successor"]["end"] == 2024


def test_compute_periods_still_in_office_has_no_transition():
    admin = Administration(
        leader_name="Y", country="Brazil", country_iso3="BRA",
        start_date=datetime(2023, 1, 1), end_date=None,
    )
    p = compute_periods(admin)
    assert "transition" not in p
    assert p["administration"]["start"] == 2023


def test_normalize_direction():
    values = {2018: 10.0, 2019: 20.0, 2020: 30.0}
    # higher_better: max value -> 100, min -> 0
    assert _normalize(30.0, values, "higher_better") == 100.0
    assert _normalize(10.0, values, "higher_better") == 0.0
    # lower_better flips it
    assert _normalize(10.0, values, "lower_better") == 100.0
    assert _normalize(30.0, values, "lower_better") == 0.0


def test_normalize_handles_empty():
    assert _normalize(5.0, {}, "higher_better") is None
    assert _normalize(None, {2020: 1.0}, "higher_better") is None
