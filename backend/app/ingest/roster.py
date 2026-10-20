"""Roster of real leaders to ingest, mapped to public source identifiers.

Wikipedia titles are the primary evidence source (public + cited). `news_query`
is used by the GDELT / news collectors when reachable. Add or edit entries here;
nothing about a real person is asserted in code — evidence comes from sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Google News locales to query per country: local + international (en-US always).
COUNTRY_LOCALES: dict[str, list[tuple[str, str]]] = {
    "Brazil": [("en-US", "US"), ("pt-BR", "BR")],
    "United States": [("en-US", "US")],
    "Russia": [("en-US", "US"), ("ru-RU", "RU")],
    "China": [("en-US", "US"), ("zh-CN", "CN")],
    "North Korea": [("en-US", "US"), ("ko-KR", "KR")],
    "Israel": [("en-US", "US"), ("he-IL", "IL")],
    "Palestine": [("en-US", "US"), ("ar-EG", "EG")],
    "Ireland": [("en-US", "US"), ("en-IE", "IE")],
    "United Kingdom": [("en-US", "US"), ("en-GB", "GB")],
}


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
    name_terms: list[str] = field(default_factory=list)

    def locales(self) -> list[tuple[str, str]]:
        return COUNTRY_LOCALES.get(self.country, [("en-US", "US")])

    def terms(self) -> list[str]:
        if self.name_terms:
            return self.name_terms
        parts = self.name.split()
        return [self.name] + ([parts[-1]] if len(parts) > 1 else [])


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
    "joe-biden": LeaderSpec(
        slug="joe-biden", name="Joe Biden", country="United States",
        region="North America", continent="North America",
        political_affiliation="Democratic Party", current=0, office="Former President",
        wikipedia=[("en", "Joe Biden")], news_query='"Joe Biden"',
    ),
    "kamala-harris": LeaderSpec(
        slug="kamala-harris", name="Kamala Harris", country="United States",
        region="North America", continent="North America",
        political_affiliation="Democratic Party", current=0, office="Vice President",
        wikipedia=[("en", "Kamala Harris")], news_query='"Kamala Harris"',
    ),
    "joe-biden": LeaderSpec(
        slug="joe-biden", name="Joe Biden", country="United States",
        region="North America", continent="North America",
        political_affiliation="Democratic Party", current=0, office="Former President",
        wikipedia=[("en", "Joe Biden")], news_query='"Joe Biden"',
    ),
    "barack-obama": LeaderSpec(
        slug="barack-obama", name="Barack Obama", country="United States",
        region="North America", continent="North America",
        political_affiliation="Democratic Party", current=0, office="Former President",
        wikipedia=[("en", "Barack Obama")], news_query='"Barack Obama"',
    ),
    "george-w-bush": LeaderSpec(
        slug="george-w-bush", name="George W. Bush", country="United States",
        region="North America", continent="North America",
        political_affiliation="Republican Party", current=0, office="Former President",
        wikipedia=[("en", "George W. Bush")], news_query='"George W. Bush"',
    ),
    "bill-clinton": LeaderSpec(
        slug="bill-clinton", name="Bill Clinton", country="United States",
        region="North America", continent="North America",
        political_affiliation="Democratic Party", current=0, office="Former President",
        wikipedia=[("en", "Bill Clinton")], news_query='"Bill Clinton"',
    ),
    "ronald-reagan": LeaderSpec(
        slug="ronald-reagan", name="Ronald Reagan", country="United States",
        region="North America", continent="North America",
        political_affiliation="Republican Party", current=0, office="Former President",
        wikipedia=[("en", "Ronald Reagan")], news_query='"Ronald Reagan"',
    ),
    "vladimir-putin": LeaderSpec(
        slug="vladimir-putin", name="Vladimir Putin", country="Russia",
        region="Eastern Europe", continent="Europe",
        political_affiliation="Independent / United Russia", current=1, office="President",
        wikipedia=[("en", "Vladimir Putin")], news_query='"Vladimir Putin"',
    ),
    "dmitry-medvedev": LeaderSpec(
        slug="dmitry-medvedev", name="Dmitry Medvedev", country="Russia",
        region="Eastern Europe", continent="Europe",
        political_affiliation="United Russia", current=0, office="Former President",
        wikipedia=[("en", "Dmitry Medvedev")], news_query='"Dmitry Medvedev"',
    ),
    "xi-jinping": LeaderSpec(
        slug="xi-jinping", name="Xi Jinping", country="China",
        region="East Asia", continent="Asia",
        political_affiliation="Chinese Communist Party", current=1, office="President",
        wikipedia=[("en", "Xi Jinping")], news_query='"Xi Jinping"',
    ),
    "hu-jintao": LeaderSpec(
        slug="hu-jintao", name="Hu Jintao", country="China",
        region="East Asia", continent="Asia",
        political_affiliation="Chinese Communist Party", current=0, office="Former President",
        wikipedia=[("en", "Hu Jintao")], news_query='"Hu Jintao"',
    ),
    "kim-jong-un": LeaderSpec(
        slug="kim-jong-un", name="Kim Jong Un", country="North Korea",
        region="East Asia", continent="Asia",
        political_affiliation="Workers' Party of Korea", current=1, office="Supreme Leader",
        wikipedia=[("en", "Kim Jong Un")], news_query='"Kim Jong Un"',
    ),
    "kim-jong-il": LeaderSpec(
        slug="kim-jong-il", name="Kim Jong Il", country="North Korea",
        region="East Asia", continent="Asia",
        political_affiliation="Workers' Party of Korea", current=0, office="Former Supreme Leader",
        wikipedia=[("en", "Kim Jong Il")], news_query='"Kim Jong Il"',
    ),
    "isaac-herzog": LeaderSpec(
        slug="isaac-herzog", name="Isaac Herzog", country="Israel",
        region="Middle East", continent="Asia",
        political_affiliation="Independent (formerly Labor)", current=1, office="President",
        wikipedia=[("en", "Isaac Herzog")], news_query='"Isaac Herzog"',
    ),
    "reuven-rivlin": LeaderSpec(
        slug="reuven-rivlin", name="Reuven Rivlin", country="Israel",
        region="Middle East", continent="Asia",
        political_affiliation="Likud", current=0, office="Former President",
        wikipedia=[("en", "Reuven Rivlin")], news_query='"Reuven Rivlin"',
    ),
    "shimon-peres": LeaderSpec(
        slug="shimon-peres", name="Shimon Peres", country="Israel",
        region="Middle East", continent="Asia",
        political_affiliation="Kadima", current=0, office="Former President",
        wikipedia=[("en", "Shimon Peres")], news_query='"Shimon Peres"',
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
    "simon-harris": LeaderSpec(
        slug="simon-harris", name="Simon Harris", country="Ireland",
        region="Western Europe", continent="Europe",
        political_affiliation="Fine Gael", current=0, office="Former Taoiseach",
        wikipedia=[("en", "Simon Harris (Irish politician)")], news_query='"Simon Harris" Ireland',
    ),
    "sean-gallagher": LeaderSpec(
        slug="sean-gallagher", name="Seán Gallagher", country="Ireland",
        region="Western Europe", continent="Europe",
        political_affiliation="Independent", current=0, office="Presidential Candidate",
        wikipedia=[("en", "Seán Gallagher (Irish politician)")], news_query='"Seán Gallagher" Ireland presidential',
    ),
    "peter-casey": LeaderSpec(
        slug="peter-casey", name="Peter Casey", country="Ireland",
        region="Western Europe", continent="Europe",
        political_affiliation="Independent", current=0, office="Presidential Candidate",
        wikipedia=[("en", "Peter Casey (Irish politician)")], news_query='"Peter Casey" Ireland presidential',
    ),
    "keir-starmer": LeaderSpec(
        slug="keir-starmer", name="Keir Starmer", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Labour Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Keir Starmer")], news_query='"Keir Starmer"',
    ),
    "rishi-sunak": LeaderSpec(
        slug="rishi-sunak", name="Rishi Sunak", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Conservative Party", current=0, office="Former Prime Minister",
        wikipedia=[("en", "Rishi Sunak")], news_query='"Rishi Sunak"',
    ),
    "boris-johnson": LeaderSpec(
        slug="boris-johnson", name="Boris Johnson", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Conservative Party", current=0, office="Former Prime Minister",
        wikipedia=[("en", "Boris Johnson")], news_query='"Boris Johnson"',
    ),
    "theresa-may": LeaderSpec(
        slug="theresa-may", name="Theresa May", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Conservative Party", current=0, office="Former Prime Minister",
        wikipedia=[("en", "Theresa May")], news_query='"Theresa May"',
    ),
    "david-cameron": LeaderSpec(
        slug="david-cameron", name="David Cameron", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Conservative Party", current=0, office="Former Prime Minister",
        wikipedia=[("en", "David Cameron")], news_query='"David Cameron"',
    ),
    "gordon-brown": LeaderSpec(
        slug="gordon-brown", name="Gordon Brown", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Labour Party", current=0, office="Former Prime Minister",
        wikipedia=[("en", "Gordon Brown")], news_query='"Gordon Brown"',
    ),
    "tony-blair": LeaderSpec(
        slug="tony-blair", name="Tony Blair", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Labour Party", current=0, office="Former Prime Minister",
        wikipedia=[("en", "Tony Blair")], news_query='"Tony Blair"',
    ),
    "charles-iii": LeaderSpec(
        slug="charles-iii", name="Charles III", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Monarchy (non-partisan)", current=1, office="King",
        wikipedia=[("en", "Charles III")], news_query='"King Charles III"',
    ),
    "elizabeth-ii": LeaderSpec(
        slug="elizabeth-ii", name="Elizabeth II", country="United Kingdom",
        region="Western Europe", continent="Europe",
        political_affiliation="Monarchy (non-partisan)", current=0, office="Former Queen",
        wikipedia=[("en", "Elizabeth II")], news_query='"Elizabeth II"',
    ),
}

PILOT_SLUGS = [s for s, spec in ROSTER.items() if spec.pilot]
