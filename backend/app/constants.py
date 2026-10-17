"""Domain constants: categories, evidence classification weights, source ratings.

These encode the platform methodology so that every score is reproducible from
the stored evidence. The AI never assigns legal guilt; it evaluates documented
public evidence and source weighting to produce a transparency score.
"""

# ---------------------------------------------------------------------------
# Scoring categories (from the platform specification)
# ---------------------------------------------------------------------------
CATEGORIES = [
    "Corruption",
    "Crime",
    "Environmental Crime",
    "Male Chauvinism",
    "Homophobia",
    "Personal Integrity",
    "Court Proceedings",
    "Scandals",
    "Human Rights",
    "Democratic Integrity",
]

# Categories that demand extra caution (controversial topics policy).
# For these we prioritise verified/court/official evidence and heavily
# discount single-source or purely political accusations.
CONTROVERSIAL_CATEGORIES = {
    "Corruption",
    "Crime",
    "Environmental Crime",
    "Male Chauvinism",
    "Homophobia",
    "Personal Integrity",
    "Court Proceedings",
    "Scandals",
    "Human Rights",
}

# ---------------------------------------------------------------------------
# Evidence classification -> intrinsic reliability weight (0..1)
# ---------------------------------------------------------------------------
EVIDENCE_TYPES = {
    "VERIFIED FACT": 1.00,
    "OFFICIAL RECORD": 0.95,
    "COURT RECORD": 0.95,
    "ONGOING INVESTIGATION": 0.75,
    "FACT CHECK": 0.80,
    "NGO REPORT": 0.75,
    "INTERNATIONAL REPORT": 0.80,
    "GOVERNMENT DATA": 0.85,
    "POLICY DECISION": 0.70,
    "PUBLIC STATEMENT": 0.60,
    "MEDIA REPORT": 0.60,
    "REPORTED ALLEGATION": 0.45,
    "DISPUTED CLAIM": 0.30,
    "UNVERIFIED CLAIM": 0.20,
}

DEFAULT_EVIDENCE_WEIGHT = 0.4

# ---------------------------------------------------------------------------
# Known source reliability ratings (0..1). Unknown sources default lower.
# ---------------------------------------------------------------------------
SOURCE_RATINGS = {
    "Court Records": 0.98,
    "Supreme Court": 0.98,
    "Official Gazette": 0.95,
    "Government Data": 0.90,
    "Transparency International": 0.92,
    "Amnesty International": 0.88,
    "Human Rights Watch": 0.88,
    "United Nations": 0.90,
    "OECD": 0.90,
    "Reuters": 0.90,
    "Associated Press": 0.90,
    "BBC": 0.88,
    "The Guardian": 0.80,
    "The New York Times": 0.82,
    "Financial Times": 0.84,
    "Bloomberg": 0.84,
    "Al Jazeera": 0.75,
    "Local Media": 0.55,
    "Social Media": 0.25,
    "Anonymous Blog": 0.15,
}

DEFAULT_SOURCE_RATING = 0.5

# Trust & Confidence engine weights (must sum to 1.0).
TRUST_WEIGHTS = {
    "source_quality": 0.40,
    "source_quantity": 0.25,
    "recency": 0.20,
    "consistency": 0.15,
}
