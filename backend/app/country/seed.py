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
    dict(leader_name="Flávio Bolsonaro", country="Brazil", country_iso3="BRA",
         office="Senator", party="Liberal Party (PL)", region="South America",
         continent="South America", start_date="2019-02-01", end_date=None,
         predecessor_name="Romário", successor_name=None),
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
    dict(leader_name="Michael D. Higgins", country="Ireland", country_iso3="IRL",
         office="President", party="Independent (formerly Labour)", region="Western Europe",
         continent="Europe", start_date="2011-11-11", end_date=None,
         predecessor_name="Mary McAleese", successor_name=None),
    # France
    dict(leader_name="Emmanuel Macron", country="France", country_iso3="FRA",
         office="President", party="Renaissance", region="Western Europe",
         continent="Europe", start_date="2017-05-14", end_date=None,
         predecessor_name="François Hollande", successor_name=None),
    # Germany
    dict(leader_name="Olaf Scholz", country="Germany", country_iso3="DEU",
         office="Chancellor", party="Social Democratic Party", region="Western Europe",
         continent="Europe", start_date="2021-12-08", end_date=None,
         predecessor_name="Angela Merkel", successor_name=None),
    # Italy
    dict(leader_name="Giorgia Meloni", country="Italy", country_iso3="ITA",
         office="Prime Minister", party="Brothers of Italy", region="Southern Europe",
         continent="Europe", start_date="2022-10-22", end_date=None,
         predecessor_name="Mario Draghi", successor_name=None),
    # Japan
    dict(leader_name="Fumio Kishida", country="Japan", country_iso3="JPN",
         office="Prime Minister", party="Liberal Democratic Party", region="East Asia",
         continent="Asia", start_date="2021-10-04", end_date=None,
         predecessor_name="Yoshihide Suga", successor_name=None),
    # Canada
    dict(leader_name="Justin Trudeau", country="Canada", country_iso3="CAN",
         office="Prime Minister", party="Liberal Party", region="North America",
         continent="North America", start_date="2015-11-04", end_date=None,
         predecessor_name="Stephen Harper", successor_name=None),
    # India
    dict(leader_name="Narendra Modi", country="India", country_iso3="IND",
         office="Prime Minister", party="Bharatiya Janata Party", region="South Asia",
         continent="Asia", start_date="2014-05-26", end_date=None,
         predecessor_name="Manmohan Singh", successor_name=None),
    # South Africa
    dict(leader_name="Cyril Ramaphosa", country="South Africa", country_iso3="ZAF",
         office="President", party="African National Congress", region="Southern Africa",
         continent="Africa", start_date="2018-02-15", end_date=None,
         predecessor_name="Jacob Zuma", successor_name=None),
    # Russia
    dict(leader_name="Vladimir Putin", country="Russia", country_iso3="RUS",
         office="President", party="Independent / United Russia", region="Eastern Europe",
         continent="Europe", start_date="2012-05-07", end_date=None,
         predecessor_name="Dmitry Medvedev", successor_name=None),
    # China
    dict(leader_name="Xi Jinping", country="China", country_iso3="CHN",
         office="President", party="Chinese Communist Party", region="East Asia",
         continent="Asia", start_date="2013-03-14", end_date=None,
         predecessor_name="Hu Jintao", successor_name=None),
    # Israel
    dict(leader_name="Benjamin Netanyahu", country="Israel", country_iso3="ISR",
         office="Prime Minister", party="Likud", region="Middle East",
         continent="Asia", start_date="2022-12-29", end_date=None,
         predecessor_name="Yair Lapid", successor_name=None),
    dict(leader_name="Isaac Herzog", country="Israel", country_iso3="ISR",
         office="President", party="Independent (formerly Labor)", region="Middle East",
         continent="Asia", start_date="2021-07-07", end_date=None,
         predecessor_name="Reuven Rivlin", successor_name=None),
    # Turkey
    dict(leader_name="Recep Tayyip Erdoğan", country="Turkey", country_iso3="TUR",
         office="President", party="Justice and Development Party", region="Middle East",
         continent="Asia", start_date="2014-08-28", end_date=None,
         predecessor_name="Abdullah Gül", successor_name=None),
    # Saudi Arabia
    dict(leader_name="Mohammed bin Salman", country="Saudi Arabia", country_iso3="SAU",
         office="Crown Prince", party="House of Saud", region="Middle East",
         continent="Asia", start_date="2017-06-21", end_date=None,
         predecessor_name="Mohammed bin Nayef", successor_name=None),
    # Indonesia
    dict(leader_name="Joko Widodo", country="Indonesia", country_iso3="IDN",
         office="President", party="Indonesian Democratic Party of Struggle", region="Southeast Asia",
         continent="Asia", start_date="2014-10-20", end_date=None,
         predecessor_name="Susilo Bambang Yudhoyono", successor_name=None),
    # Mexico
    dict(leader_name="Andrés Manuel López Obrador", country="Mexico", country_iso3="MEX",
         office="President", party="Morena", region="North America",
         continent="North America", start_date="2018-12-01", end_date=None,
         predecessor_name="Enrique Peña Nieto", successor_name=None),
    # Philippines
    dict(leader_name="Ferdinand Marcos Jr.", country="Philippines", country_iso3="PHL",
         office="President", party="Partido Federal ng Pilipinas", region="Southeast Asia",
         continent="Asia", start_date="2022-06-30", end_date=None,
         predecessor_name="Rodrigo Duterte", successor_name=None),
    # South Korea
    dict(leader_name="Yoon Suk Yeol", country="South Korea", country_iso3="KOR",
         office="President", party="People Power Party", region="East Asia",
         continent="Asia", start_date="2022-05-10", end_date=None,
         predecessor_name="Moon Jae-in", successor_name=None),
    # Singapore
    dict(leader_name="Lee Hsien Loong", country="Singapore", country_iso3="SGP",
         office="Prime Minister", party="People's Action Party", region="Southeast Asia",
         continent="Asia", start_date="2004-08-12", end_date=None,
         predecessor_name="Goh Chok Tong", successor_name=None),
    # Bangladesh
    dict(leader_name="Sheikh Hasina", country="Bangladesh", country_iso3="BGD",
         office="Prime Minister", party="Awami League", region="South Asia",
         continent="Asia", start_date="2009-01-06", end_date=None,
         predecessor_name="Fazlul Haque", successor_name=None),
    # Chile
    dict(leader_name="Gabriel Boric", country="Chile", country_iso3="CHL",
         office="President", party="Social Convergence", region="South America",
         continent="South America", start_date="2022-03-11", end_date=None,
         predecessor_name="Sebastián Piñera", successor_name=None),
    # Colombia
    dict(leader_name="Gustavo Petro", country="Colombia", country_iso3="COL",
         office="President", party="Historic Pact for Colombia", region="South America",
         continent="South America", start_date="2022-08-07", end_date=None,
         predecessor_name="Iván Duque", successor_name=None),
    # Egypt
    dict(leader_name="Abdel Fattah el-Sisi", country="Egypt", country_iso3="EGY",
         office="President", party="Independent", region="North Africa",
         continent="Africa", start_date="2014-06-08", end_date=None,
         predecessor_name="Mohamed Morsi", successor_name=None),
]


def seed_administrations(db: Session) -> None:
    for a in ADMINISTRATIONS:
        # Check if this administration already exists
        existing = db.query(models.Administration).filter(
            models.Administration.leader_name == a["leader_name"],
            models.Administration.country == a["country"],
            models.Administration.start_date == datetime.fromisoformat(a["start_date"])
        ).first()
        
        if not existing:
            db.add(models.Administration(
                leader_name=a["leader_name"], country=a["country"], country_iso3=a["country_iso3"],
                office=a["office"], party=a["party"], region=a["region"], continent=a["continent"],
                start_date=datetime.fromisoformat(a["start_date"]),
                end_date=datetime.fromisoformat(a["end_date"]) if a["end_date"] else None,
                predecessor_name=a["predecessor_name"], successor_name=a["successor_name"],
            ))
    db.commit()
