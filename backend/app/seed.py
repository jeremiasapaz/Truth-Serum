"""Seed the database with SYNTHETIC / FICTIONAL demonstration data.

All leaders, countries and evidence below are fictional and exist only to
exercise the platform (dashboard, filters, comparison, charts, evidence audit).
They are NOT claims about any real person. Replace with vetted, sourced records
for real use.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from . import models
from .constants import SOURCE_RATINGS, DEFAULT_SOURCE_RATING, CATEGORIES
from .scoring import EvidenceInput, compute_score


def _rating(name: str) -> float:
    return SOURCE_RATINGS.get(name, DEFAULT_SOURCE_RATING)


def E(category, classification, polarity, title, text, source, date, url=None):
    return {
        "category": category,
        "classification": classification,
        "polarity": polarity,
        "title": title,
        "extracted_text": text,
        "source_name": source,
        "source_url": url or f"https://example.org/{source.lower().replace(' ', '-')}",
        "source_rating": _rating(source),
        "published_at": datetime.fromisoformat(date),
    }


LEADERS = [
    {
        "name": "Elena Vasquez",
        "country": "Maravia",
        "region": "Southern Maravia",
        "continent": "South America",
        "political_affiliation": "Progressive Alliance",
        "current": 1,
        "bio": "Fictional president of the fictional republic of Maravia. Demo data only.",
        "evidence": [
            E("Corruption", "COURT RECORD", -1, "Procurement inquiry filed",
              "A fictional court docket lists an inquiry into a public works contract.",
              "Court Records", "2023-05-11"),
            E("Corruption", "MEDIA REPORT", -1, "Reports of inflated contracts",
              "Fictional outlet reports allegations of inflated infrastructure contracts.",
              "Reuters", "2023-06-02"),
            E("Human Rights", "NGO REPORT", 1, "Expanded healthcare access",
              "Fictional NGO notes expanded rural healthcare coverage.",
              "Amnesty International", "2022-09-15"),
            E("Democratic Integrity", "OFFICIAL RECORD", 1, "Free and fair election certified",
              "Fictional electoral commission certified the national vote.",
              "United Nations", "2021-11-20"),
            E("Environmental Crime", "GOVERNMENT DATA", 1, "Deforestation down 12%",
              "Fictional environment ministry data shows reduced deforestation.",
              "Government Data", "2023-01-30"),
            E("Scandals", "DISPUTED CLAIM", -1, "Alleged resort stay",
              "A disputed social-media claim about a private holiday.",
              "Social Media", "2023-07-04"),
        ],
    },
    {
        "name": "Markus Thorne",
        "country": "Veldoria",
        "region": "North Veldoria",
        "continent": "Europe",
        "political_affiliation": "National Conservative Party",
        "current": 0,
        "bio": "Fictional former prime minister of Veldoria. Demo data only.",
        "evidence": [
            E("Corruption", "COURT RECORD", -1, "Convicted in fictional bribery case",
              "Fictional appellate court upheld a bribery conviction.",
              "Court Records", "2020-03-18"),
            E("Corruption", "INTERNATIONAL REPORT", -1, "Flagged by watchdog index",
              "Fictional watchdog flagged governance concerns.",
              "Transparency International", "2019-12-01"),
            E("Crime", "ONGOING INVESTIGATION", -1, "Campaign finance probe",
              "A fictional ongoing probe into campaign finance.",
              "BBC", "2020-05-22"),
            E("Homophobia", "PUBLIC STATEMENT", -1, "Opposed equality bill",
              "Fictional public statements opposing an equality bill.",
              "The Guardian", "2018-02-10"),
            E("Scandals", "MEDIA REPORT", -1, "Cabinet resignation scandal",
              "Fictional cabinet reshuffle amid scandal.",
              "Associated Press", "2019-08-09"),
            E("Human Rights", "NGO REPORT", -1, "Press freedom concerns",
              "Fictional NGO raised press-freedom concerns.",
              "Human Rights Watch", "2019-04-17"),
        ],
    },
    {
        "name": "Aiko Tanaka",
        "country": "Keshima",
        "region": "East Keshima",
        "continent": "Asia",
        "political_affiliation": "Civic Renewal",
        "current": 1,
        "bio": "Fictional president of Keshima known for transparency reforms. Demo data only.",
        "evidence": [
            E("Corruption", "OFFICIAL RECORD", 1, "Passed asset-disclosure law",
              "Fictional law requiring officials to disclose assets.",
              "Official Gazette", "2022-04-12"),
            E("Democratic Integrity", "INTERNATIONAL REPORT", 1, "Strong institutions rating",
              "Fictional index rates institutions highly.",
              "OECD", "2023-02-01"),
            E("Environmental Crime", "GOVERNMENT DATA", 1, "Net-zero roadmap on track",
              "Fictional progress on emissions targets.",
              "Government Data", "2023-03-11"),
            E("Human Rights", "NGO REPORT", 1, "Improved detention standards",
              "Fictional NGO praised detention reforms.",
              "Amnesty International", "2022-10-05"),
            E("Scandals", "FACT CHECK", 0, "Viral claim debunked",
              "A fictional viral claim was fact-checked as false.",
              "Reuters", "2023-05-30"),
            E("Personal Integrity", "VERIFIED FACT", 1, "Published tax returns",
              "Fictional publication of full tax returns.",
              "Official Gazette", "2023-01-09"),
        ],
    },
    {
        "name": "Dmitri Kovalenko",
        "country": "Rusalka",
        "region": "Central Rusalka",
        "continent": "Europe",
        "political_affiliation": "Unity Front",
        "current": 1,
        "bio": "Fictional leader of Rusalka. Demo data only.",
        "evidence": [
            E("Human Rights", "INTERNATIONAL REPORT", -1, "Crackdown on protests reported",
              "Fictional international report on protest crackdowns.",
              "United Nations", "2023-09-02"),
            E("Democratic Integrity", "NGO REPORT", -1, "Election irregularities alleged",
              "Fictional NGO alleged irregularities.",
              "Human Rights Watch", "2022-12-19"),
            E("Crime", "ONGOING INVESTIGATION", -1, "Embezzlement inquiry",
              "A fictional ongoing embezzlement inquiry.",
              "Reuters", "2023-06-14"),
            E("Corruption", "REPORTED ALLEGATION", -1, "Offshore accounts alleged",
              "Fictional reporting alleges offshore accounts.",
              "Local Media", "2023-07-21"),
            E("Environmental Crime", "MEDIA REPORT", -1, "River pollution incident",
              "Fictional report of an industrial pollution incident.",
              "Al Jazeera", "2022-08-03"),
            E("Scandals", "UNVERIFIED CLAIM", -1, "Anonymous memo leaked",
              "An unverified anonymous memo circulated online.",
              "Anonymous Blog", "2023-10-01"),
        ],
    },
    {
        "name": "Fatima Al-Rashid",
        "country": "Zahran",
        "region": "Coastal Zahran",
        "continent": "Africa",
        "political_affiliation": "Reform Movement",
        "current": 1,
        "bio": "Fictional prime minister of Zahran. Demo data only.",
        "evidence": [
            E("Human Rights", "NGO REPORT", 1, "Expanded women's education",
              "Fictional NGO highlighted gains in girls' education.",
              "Amnesty International", "2023-03-22"),
            E("Male Chauvinism", "PUBLIC STATEMENT", 1, "Championed equal-pay law",
              "Fictional public push for equal-pay legislation.",
              "BBC", "2022-11-08"),
            E("Corruption", "FACT CHECK", 0, "Contract claim unproven",
              "A fictional contract claim could not be substantiated.",
              "Reuters", "2023-04-19"),
            E("Environmental Crime", "GOVERNMENT DATA", 1, "Solar expansion program",
              "Fictional national solar expansion data.",
              "Government Data", "2023-02-27"),
            E("Scandals", "MEDIA REPORT", 0, "Minor travel-expense query",
              "Fictional minor query over travel expenses, later clarified.",
              "Financial Times", "2023-06-30"),
            E("Democratic Integrity", "OFFICIAL RECORD", 1, "Peaceful power transfer",
              "Fictional certified peaceful transfer of power.",
              "United Nations", "2021-05-14"),
        ],
    },
    {
        "name": "Carlos Mendez",
        "country": "Solterra",
        "region": "West Solterra",
        "continent": "North America",
        "political_affiliation": "Liberty Coalition",
        "current": 0,
        "bio": "Fictional former president of Solterra. Demo data only.",
        "evidence": [
            E("Corruption", "COURT RECORD", -1, "Indicted on fictional fraud charges",
              "Fictional indictment on fraud charges.",
              "Court Records", "2021-07-07"),
            E("Crime", "COURT RECORD", -1, "Obstruction charge filed",
              "Fictional obstruction charge filed in court.",
              "Supreme Court", "2021-09-23"),
            E("Scandals", "MEDIA REPORT", -1, "Multiple overlapping scandals",
              "Fictional reporting on several overlapping scandals.",
              "The New York Times", "2020-10-11"),
            E("Personal Integrity", "REPORTED ALLEGATION", -1, "Conflict-of-interest claims",
              "Fictional conflict-of-interest allegations.",
              "Bloomberg", "2020-11-02"),
            E("Human Rights", "NGO REPORT", 0, "Mixed record on asylum",
              "Fictional NGO described a mixed asylum record.",
              "Human Rights Watch", "2020-06-16"),
            E("Environmental Crime", "INTERNATIONAL REPORT", -1, "Rolled back protections",
              "Fictional report on rolled-back environmental protections.",
              "OECD", "2019-12-12"),
        ],
    },
]


def seed_if_empty(db: Session) -> None:
    if db.query(models.Leader).count() > 0:
        return

    # Register known sources for the auditability panel.
    for name, rating in SOURCE_RATINGS.items():
        db.add(models.Source(name=name, rating=rating))

    for spec in LEADERS:
        leader = models.Leader(
            name=spec["name"],
            country=spec["country"],
            region=spec["region"],
            continent=spec["continent"],
            political_affiliation=spec["political_affiliation"],
            current=spec["current"],
            bio=spec["bio"],
        )
        db.add(leader)
        db.flush()

        by_cat: dict[str, list[EvidenceInput]] = {}
        for ev in spec["evidence"]:
            db.add(
                models.Evidence(
                    leader_id=leader.id,
                    category=ev["category"],
                    classification=ev["classification"],
                    polarity=ev["polarity"],
                    title=ev["title"],
                    extracted_text=ev["extracted_text"],
                    source_name=ev["source_name"],
                    source_url=ev["source_url"],
                    source_rating=ev["source_rating"],
                    published_at=ev["published_at"],
                )
            )
            by_cat.setdefault(ev["category"], []).append(
                EvidenceInput(
                    classification=ev["classification"],
                    polarity=ev["polarity"],
                    source_name=ev["source_name"],
                    source_rating=ev["source_rating"],
                    published_at=ev["published_at"],
                )
            )

        # Initial deterministic scores (reproducible baseline).
        for category in CATEGORIES:
            result = compute_score(category, by_cat.get(category, []))
            db.add(
                models.CategoryScore(
                    leader_id=leader.id,
                    category=category,
                    score=result.score,
                    confidence=result.confidence,
                    evidence_count=result.evidence_count,
                    source_count=result.source_count,
                    source_quality=result.source_quality,
                    reason=result.reason,
                    scored_by="engine",
                )
            )
            db.add(
                models.ScoreHistory(
                    leader_id=leader.id,
                    category=category,
                    score=result.score,
                    confidence=result.confidence,
                )
            )

    db.commit()
