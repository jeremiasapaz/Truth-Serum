"""Roster of real leaders to ingest, mapped to public source identifiers.

Wikipedia titles are the primary evidence source (public + cited). `news_query`
is used by the GDELT / news collectors when reachable. Add or edit entries here;
nothing about a real person is asserted in code — evidence comes from sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LeaderSpec:
    slug: str
    name: str
    country: str
    region: str
    continent: str
    political_affiliation: str
    current: int
    office: str
    wikipedia: list[tuple[str, str]]  # [(lang, title), ...]
    news_query: str
    bio: str = ""
    pilot: bool = False
    extra_domains: list[str] = field(default_factory=list)


ROSTER: dict[str, LeaderSpec] = {
    # --- PILOT -------------------------------------------------------------
    "lula": LeaderSpec(
        slug="lula", name="Luiz Inácio Lula da Silva", country="Brazil",
        region="South America", continent="South America",
        political_affiliation="Workers' Party (PT)", current=1, office="President",
        wikipedia=[("en", "Luiz Inácio Lula da Silva")],
        news_query='"Lula da Silva"', pilot=True,
    ),
    "jair-bolsonaro": LeaderSpec(
        slug="jair-bolsonaro", name="Jair Bolsonaro", country="Brazil",
        region="South America", continent="South America",
        political_affiliation="Liberal Party (PL)", current=0, office="Former President",
        wikipedia=[("en", "Jair Bolsonaro")],
        news_query='"Jair Bolsonaro"', pilot=True,
    ),
    "flavio-bolsonaro": LeaderSpec(
        slug="flavio-bolsonaro", name="Flávio Bolsonaro", country="Brazil",
        region="South America", continent="South America",
        political_affiliation="Liberal Party (PL)", current=1, office="Senator",
        wikipedia=[("en", "Flávio Bolsonaro")],
        news_query='"Flavio Bolsonaro"', pilot=True,
    ),

    # --- REST OF REQUESTED ROSTER (ready to ingest, not in pilot) ---------
    "donald-trump": LeaderSpec(
        slug="donald-trump", name="Donald Trump", country="United States",
        region="North America", continent="North America",
        political_affiliation="Republican Party", current=1, office="President",
        wikipedia=[("en", "Donald Trump")], news_query='"Donald Trump"',
    ),
    "vladimir-putin": LeaderSpec(
        slug="vladimir-putin", name="Vladimir Putin", country="Russia",
        region="Eastern Europe", continent="Europe",
        political_affiliation="Independent / United Russia", current=1, office="President",
        wikipedia=[("en", "Vladimir Putin")], news_query='"Vladimir Putin"',
    ),
    "xi-jinping": LeaderSpec(
        slug="xi-jinping", name="Xi Jinping", country="China",
        region="East Asia", continent="Asia",
        political_affiliation="Chinese Communist Party", current=1, office="President",
        wikipedia=[("en", "Xi Jinping")], news_query='"Xi Jinping"',
    ),
    "kim-jong-un": LeaderSpec(
        slug="kim-jong-un", name="Kim Jong Un", country="North Korea",
        region="East Asia", continent="Asia",
        political_affiliation="Workers' Party of Korea", current=1, office="Supreme Leader",
        wikipedia=[("en", "Kim Jong Un")], news_query='"Kim Jong Un"',
    ),
    "isaac-herzog": LeaderSpec(
        slug="isaac-herzog", name="Isaac Herzog", country="Israel",
        region="Middle East", continent="Asia",
        political_affiliation="Independent (formerly Labor)", current=1, office="President",
        wikipedia=[("en", "Isaac Herzog")], news_query='"Isaac Herzog"',
    ),
    "mahmoud-abbas": LeaderSpec(
        slug="mahmoud-abbas", name="Mahmoud Abbas", country="Palestine",
        region="Middle East", continent="Asia",
        political_affiliation="Fatah", current=1, office="President (PA)",
        wikipedia=[("en", "Mahmoud Abbas")], news_query='"Mahmoud Abbas"',
    ),
    "mohammad-mustafa": LeaderSpec(
        slug="mohammad-mustafa", name="Mohammad Mustafa", country="Palestine",
        region="Middle East", continent="Asia",
        political_affiliation="Independent", current=1, office="Prime Minister (PA)",
        wikipedia=[("en", "Mohammad Mustafa (economist)")], news_query='"Mohammad Mustafa" Palestinian',
    ),
    "micheal-martin": LeaderSpec(
        slug="micheal-martin", name="Micheál Martin", country="Ireland",
        region="Western Europe", continent="Europe",
        political_affiliation="Fianna Fáil", current=1, office="Taoiseach",
        wikipedia=[("en", "Micheál Martin")], news_query='"Micheal Martin" Taoiseach',
    ),
    "michael-d-higgins": LeaderSpec(
        slug="michael-d-higgins", name="Michael D. Higgins", country="Ireland",
        region="Western Europe", continent="Europe",
        political_affiliation="Independent (formerly Labour)", current=1, office="President",
        wikipedia=[("en", "Michael D. Higgins")], news_query='"Michael D. Higgins"',
    ),
    "keir-starmer": LeaderSpec(
        slug="keir-starmer", name="Keir Starmer", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Labour Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Keir Starmer")], news_query='"Keir Starmer"',
    ),
    "charles-iii": LeaderSpec(
        slug="charles-iii", name="Charles III", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Monarchy (non-partisan)", current=1, office="King",
        wikipedia=[("en", "Charles III")], news_query='"King Charles III"',
    ),
}

PILOT_SLUGS = [s for s, spec in ROSTER.items() if spec.pilot]
