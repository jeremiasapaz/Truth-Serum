"""Seed real administrations (terms of office) for the performance engine.

These are factual office-holding dates (public record), not evaluative claims.
They enable the example comparisons: Lula vs Bolsonaro, Biden vs Trump,
Starmer vs Sunak.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .. import models

ADMINISTRATIONS = [
    # Brazil
    dict(leader_name="Jair Bolsonaro", country="Brazil", country_iso3="BRA",
         office="President", party="Liberal Party (PL)", region="South America",
         continent="South America", start_date="2019-01-01", end_date="2022-12-31",
         predecessor_name="Michel Temer", successor_name="Luiz Inácio Lula da Silva"),
    dict(leader_name="Luiz Inácio Lula da Silva", country="Brazil", country_iso3="BRA",
         office="President", party="Workers' Party (PT)", region="South America",
         continent="South America", start_date="2023-01-01", end_date=None,
         predecessor_name="Jair Bolsonaro", successor_name=None),
    # United States
    dict(leader_name="Donald Trump", country="United States", country_iso3="USA",
         office="President", party="Republican Party", region="North America",
         continent="North America", start_date="2017-01-20", end_date="2021-01-20",
         predecessor_name="Barack Obama", successor_name="Joe Biden"),
    dict(leader_name="Joe Biden", country="United States", country_iso3="USA",
         office="President", party="Democratic Party", region="North America",
         continent="North America", start_date="2021-01-20", end_date="2025-01-20",
         predecessor_name="Donald Trump", successor_name="Donald Trump"),
    dict(leader_name="Donald Trump (2nd term)", country="United States", country_iso3="USA",
         office="President", party="Republican Party", region="North America",
         continent="North America", start_date="2025-01-20", end_date=None,
         predecessor_name="Joe Biden", successor_name=None),
    # United Kingdom
    dict(leader_name="Rishi Sunak", country="United Kingdom", country_iso3="GBR",
         office="Prime Minister", party="Conservative Party", region="Western Europe",
         continent="Europe", start_date="2022-10-25", end_date="2024-07-05",
         predecessor_name="Liz Truss", successor_name="Keir Starmer"),
    dict(leader_name="Keir Starmer", country="United Kingdom", country_iso3="GBR",
         office="Prime Minister", party="Labour Party", region="Western Europe",
         continent="Europe", start_date="2024-07-05", end_date=None,
         predecessor_name="Rishi Sunak", successor_name=None),
    # Ireland
    dict(leader_name="Micheál Martin", country="Ireland", country_iso3="IRL",
         office="Taoiseach", party="Fianna Fáil", region="Western Europe",
         continent="Europe", start_date="2025-01-23", end_date=None,
         predecessor_name="Simon Harris", successor_name=None),
]


def seed_administrations(db: Session) -> None:
    if db.query(models.Administration).count() > 0:
        return
    for a in ADMINISTRATIONS:
        db.add(models.Administration(
            leader_name=a["leader_name"], country=a["country"], country_iso3=a["country_iso3"],
            office=a["office"], party=a["party"], region=a["region"], continent=a["continent"],
            start_date=datetime.fromisoformat(a["start_date"]),
            end_date=datetime.fromisoformat(a["end_date"]) if a["end_date"] else None,
            predecessor_name=a["predecessor_name"], successor_name=a["successor_name"],
        ))
    db.commit()
