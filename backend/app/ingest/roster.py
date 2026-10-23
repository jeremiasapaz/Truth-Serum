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
    "France": [("en-US", "US"), ("fr-FR", "FR")],
    "Germany": [("en-US", "US"), ("de-DE", "DE")],
    "Italy": [("en-US", "US"), ("it-IT", "IT")],
    "Japan": [("en-US", "US"), ("ja-JP", "JP")],
    "Canada": [("en-US", "US"), ("en-CA", "CA"), ("fr-CA", "CA")],
    "India": [("en-US", "US"), ("hi-IN", "IN")],
    "South Africa": [("en-US", "US"), ("af-ZA", "ZA")],
    "Egypt": [("en-US", "US"), ("ar-EG", "EG")],
    "Turkey": [("en-US", "US"), ("tr-TR", "TR")],
    "Saudi Arabia": [("en-US", "US"), ("ar-SA", "SA")],
    "European Union": [("en-US", "US"), ("fr-FR", "FR"), ("de-DE", "DE")],
    "Indonesia": [("en-US", "US"), ("id-ID", "ID")],
    "Mexico": [("en-US", "US"), ("es-MX", "MX")],
    "Philippines": [("en-US", "US"), ("tl-PH", "PH")],
    "El Salvador": [("en-US", "US"), ("es-SV", "SV")],
    "South Korea": [("en-US", "US"), ("ko-KR", "KR")],
    "Singapore": [("en-US", "US")],
    "Bangladesh": [("en-US", "US"), ("bn-BD", "BD")],
    "Pakistan": [("en-US", "US"), ("ur-PK", "PK")],
    "Syria": [("en-US", "US"), ("ar-SY", "SY")],
    "Iran": [("en-US", "US"), ("fa-IR", "IR")],
    "Rwanda": [("en-US", "US"), ("rw-RW", "RW")],
    "Kenya": [("en-US", "US"), ("sw-KE", "KE")],
    "Uganda": [("en-US", "US"), ("sw-UG", "UG")],
    "Chile": [("en-US", "US"), ("es-CL", "CL")],
    "Colombia": [("en-US", "US"), ("es-CO", "CO")],
    "Peru": [("en-US", "US"), ("es-PE", "PE")],
    "Venezuela": [("en-US", "US"), ("es-VE", "VE")],
    "Nicaragua": [("en-US", "US"), ("es-NI", "NI")],
    "Cambodia": [("en-US", "US"), ("km-KH", "KH")],
    "Myanmar": [("en-US", "US"), ("my-MM", "MM")],
    "Thailand": [("en-US", "US"), ("th-TH", "TH")],
    "United Nations": [("en-US", "US")],
    "NATO": [("en-US", "US")],
    "World Health Organization": [("en-US", "US")],
    "International Monetary Fund": [("en-US", "US")],
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
    "catherine-connolly": LeaderSpec(
        slug="catherine-connolly", name="Catherine Connolly", country="Ireland",
        region="Western Europe", continent="Europe",
        political_affiliation="Independent", current=1, office="Commissioner for Human Rights",
        wikipedia=[("en", "Catherine Connolly (Irish politician)")], news_query='"Catherine Connolly" Ireland',
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

    # --- G7 Leaders ---
    "emmanuel-macron": LeaderSpec(
        slug="emmanuel-macron", name="Emmanuel Macron", country="France",
        region="Western Europe", continent="Europe",
        political_affiliation="Renaissance", current=1, office="President",
        wikipedia=[("en", "Emmanuel Macron")], news_query='"Emmanuel Macron"',
    ),
    "olaf-scholz": LeaderSpec(
        slug="olaf-scholz", name="Olaf Scholz", country="Germany",
        region="Western Europe", continent="Europe",
        political_affiliation="Social Democratic Party", current=1, office="Chancellor",
        wikipedia=[("en", "Olaf Scholz")], news_query='"Olaf Scholz"',
    ),
    "giorgia-meloni": LeaderSpec(
        slug="giorgia-meloni", name="Giorgia Meloni", country="Italy",
        region="Southern Europe", continent="Europe",
        political_affiliation="Brothers of Italy", current=1, office="Prime Minister",
        wikipedia=[("en", "Giorgia Meloni")], news_query='"Giorgia Meloni"',
    ),
    "fumio-kishida": LeaderSpec(
        slug="fumio-kishida", name="Fumio Kishida", country="Japan",
        region="East Asia", continent="Asia",
        political_affiliation="Liberal Democratic Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Fumio Kishida")], news_query='"Fumio Kishida"',
    ),
    "justin-trudeau": LeaderSpec(
        slug="justin-trudeau", name="Justin Trudeau", country="Canada",
        region="North America", continent="North America",
        political_affiliation="Liberal Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Justin Trudeau")], news_query='"Justin Trudeau"',
    ),

    # --- BRICS+ Leaders ---
    "narendra-modi": LeaderSpec(
        slug="narendra-modi", name="Narendra Modi", country="India",
        region="South Asia", continent="Asia",
        political_affiliation="Bharatiya Janata Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Narendra Modi")], news_query='"Narendra Modi"',
    ),
    "cyril-ramaphosa": LeaderSpec(
        slug="cyril-ramaphosa", name="Cyril Ramaphosa", country="South Africa",
        region="Southern Africa", continent="Africa",
        political_affiliation="African National Congress", current=1, office="President",
        wikipedia=[("en", "Cyril Ramaphosa")], news_query='"Cyril Ramaphosa"',
    ),
    "abdel-fattah-el-sisi": LeaderSpec(
        slug="abdel-fattah-el-sisi", name="Abdel Fattah el-Sisi", country="Egypt",
        region="North Africa", continent="Africa",
        political_affiliation="Independent", current=1, office="President",
        wikipedia=[("en", "Abdel Fattah el-Sisi")], news_query='"Abdel Fattah el-Sisi"',
    ),
    "recep-tayyip-erdogan": LeaderSpec(
        slug="recep-tayyip-erdogan", name="Recep Tayyip Erdoğan", country="Turkey",
        region="Middle East", continent="Asia",
        political_affiliation="Justice and Development Party", current=1, office="President",
        wikipedia=[("en", "Recep Tayyip Erdoğan")], news_query='"Recep Tayyip Erdogan"',
    ),
    "mohammed-bin-salman": LeaderSpec(
        slug="mohammed-bin-salman", name="Mohammed bin Salman", country="Saudi Arabia",
        region="Middle East", continent="Asia",
        political_affiliation="House of Saud", current=1, office="Crown Prince",
        wikipedia=[("en", "Mohammed bin Salman")], news_query='"Mohammed bin Salman"',
    ),

    # --- European Union ---
    "ursula-von-der-leyen": LeaderSpec(
        slug="ursula-von-der-leyen", name="Ursula von der Leyen", country="European Union",
        region="Europe", continent="Europe",
        political_affiliation="European People's Party", current=1, office="President of European Commission",
        wikipedia=[("en", "Ursula von der Leyen")], news_query='"Ursula von der Leyen"',
    ),
    "charles-michel": LeaderSpec(
        slug="charles-michel", name="Charles Michel", country="European Union",
        region="Europe", continent="Europe",
        political_affiliation="Renew Europe", current=1, office="President of European Council",
        wikipedia=[("en", "Charles Michel")], news_query='"Charles Michel"',
    ),

    # --- Major Regional Powers ---
    "joko-widodo": LeaderSpec(
        slug="joko-widodo", name="Joko Widodo", country="Indonesia",
        region="Southeast Asia", continent="Asia",
        political_affiliation="Indonesian Democratic Party of Struggle", current=1, office="President",
        wikipedia=[("en", "Joko Widodo")], news_query='"Joko Widodo"',
    ),
    "andres-manuel-lopez-obrador": LeaderSpec(
        slug="andres-manuel-lopez-obrador", name="Andrés Manuel López Obrador", country="Mexico",
        region="North America", continent="North America",
        political_affiliation="Morena", current=1, office="President",
        wikipedia=[("en", "Andrés Manuel López Obrador")], news_query='"Andres Manuel Lopez Obrador"',
    ),
    "ferdinand-marcos-jr": LeaderSpec(
        slug="ferdinand-marcos-jr", name="Ferdinand Marcos Jr.", country="Philippines",
        region="Southeast Asia", continent="Asia",
        political_affiliation="Partido Federal ng Pilipinas", current=1, office="President",
        wikipedia=[("en", "Ferdinand Marcos Jr.")], news_query='"Ferdinand Marcos Jr"',
    ),
    "nayib-bukele": LeaderSpec(
        slug="nayib-bukele", name="Nayib Bukele", country="El Salvador",
        region="Central America", continent="North America",
        political_affiliation="Nuevas Ideas", current=1, office="President",
        wikipedia=[("en", "Nayib Bukele")], news_query='"Nayib Bukele"',
    ),
    "yoon-suk-yeol": LeaderSpec(
        slug="yoon-suk-yeol", name="Yoon Suk Yeol", country="South Korea",
        region="East Asia", continent="Asia",
        political_affiliation="People Power Party", current=1, office="President",
        wikipedia=[("en", "Yoon Suk Yeol")], news_query='"Yoon Suk Yeol"',
    ),
    "lee-hsien-loong": LeaderSpec(
        slug="lee-hsien-loong", name="Lee Hsien Loong", country="Singapore",
        region="Southeast Asia", continent="Asia",
        political_affiliation="People's Action Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Lee Hsien Loong")], news_query='"Lee Hsien Loong"',
    ),
    "sheikh-hasina": LeaderSpec(
        slug="sheikh-hasina", name="Sheikh Hasina", country="Bangladesh",
        region="South Asia", continent="Asia",
        political_affiliation="Awami League", current=1, office="Prime Minister",
        wikipedia=[("en", "Sheikh Hasina")], news_query='"Sheikh Hasina"',
    ),
    "imran-khan": LeaderSpec(
        slug="imran-khan", name="Imran Khan", country="Pakistan",
        region="South Asia", continent="Asia",
        political_affiliation="Pakistan Tehreek-e-Insaf", current=0, office="Former Prime Minister",
        wikipedia=[("en", "Imran Khan")], news_query='"Imran Khan"',
    ),

    # --- Middle East ---
    "bashar-al-assad": LeaderSpec(
        slug="bashar-al-assad", name="Bashar al-Assad", country="Syria",
        region="Middle East", continent="Asia",
        political_affiliation="Ba'ath Party", current=1, office="President",
        wikipedia=[("en", "Bashar al-Assad")], news_query='"Bashar al-Assad"',
    ),
    "benjamin-netanyahu": LeaderSpec(
        slug="benjamin-netanyahu", name="Benjamin Netanyahu", country="Israel",
        region="Middle East", continent="Asia",
        political_affiliation="Likud", current=1, office="Prime Minister",
        wikipedia=[("en", "Benjamin Netanyahu")], news_query='"Benjamin Netanyahu"',
    ),
    "ebrahim-raisi": LeaderSpec(
        slug="ebrahim-raisi", name="Ebrahim Raisi", country="Iran",
        region="Middle East", continent="Asia",
        political_affiliation="Principlists", current=1, office="President",
        wikipedia=[("en", "Ebrahim Raisi")], news_query='"Ebrahim Raisi"',
    ),

    # --- Africa ---
    "paul-kagame": LeaderSpec(
        slug="paul-kagame", name="Paul Kagame", country="Rwanda",
        region="East Africa", continent="Africa",
        political_affiliation="Rwandan Patriotic Front", current=1, office="President",
        wikipedia=[("en", "Paul Kagame")], news_query='"Paul Kagame"',
    ),
    "william-ruto": LeaderSpec(
        slug="william-ruto", name="William Ruto", country="Kenya",
        region="East Africa", continent="Africa",
        political_affiliation="United Democratic Alliance", current=1, office="President",
        wikipedia=[("en", "William Ruto")], news_query='"William Ruto"',
    ),
    "yoweri-museveni": LeaderSpec(
        slug="yoweri-museveni", name="Yoweri Museveni", country="Uganda",
        region="East Africa", continent="Africa",
        political_affiliation="National Resistance Movement", current=1, office="President",
        wikipedia=[("en", "Yoweri Museveni")], news_query='"Yoweri Museveni"',
    ),

    # --- Latin America ---
    "gabriel-boric": LeaderSpec(
        slug="gabriel-boric", name="Gabriel Boric", country="Chile",
        region="South America", continent="South America",
        political_affiliation="Social Convergence", current=1, office="President",
        wikipedia=[("en", "Gabriel Boric")], news_query='"Gabriel Boric"',
    ),
    "gustavo-petro": LeaderSpec(
        slug="gustavo-petro", name="Gustavo Petro", country="Colombia",
        region="South America", continent="South America",
        political_affiliation="Historic Pact for Colombia", current=1, office="President",
        wikipedia=[("en", "Gustavo Petro")], news_query='"Gustavo Petro"',
    ),
    "dina-boluarte": LeaderSpec(
        slug="dina-boluarte", name="Dina Boluarte", country="Peru",
        region="South America", continent="South America",
        political_affiliation="Alliance for Progress", current=1, office="President",
        wikipedia=[("en", "Dina Boluarte")], news_query='"Dina Boluarte"',
    ),
    "nicolas-maduro": LeaderSpec(
        slug="nicolas-maduro", name="Nicolás Maduro", country="Venezuela",
        region="South America", continent="South America",
        political_affiliation="United Socialist Party", current=1, office="President",
        wikipedia=[("en", "Nicolás Maduro")], news_query='"Nicolas Maduro"',
    ),
    "daniel-ortega": LeaderSpec(
        slug="daniel-ortega", name="Daniel Ortega", country="Nicaragua",
        region="Central America", continent="North America",
        political_affiliation="Sandinista National Liberation Front", current=1, office="President",
        wikipedia=[("en", "Daniel Ortega")], news_query='"Daniel Ortega"',
    ),

    # --- Asia-Pacific ---
    "hun-sen": LeaderSpec(
        slug="hun-sen", name="Hun Sen", country="Cambodia",
        region="Southeast Asia", continent="Asia",
        political_affiliation="Cambodian People's Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Hun Sen")], news_query='"Hun Sen"',
    ),
    "min-aung-hlaing": LeaderSpec(
        slug="min-aung-hlaing", name="Min Aung Hlaing", country="Myanmar",
        region="Southeast Asia", continent="Asia",
        political_affiliation="Tatmadaw", current=1, office="Prime Minister",
        wikipedia=[("en", "Min Aung Hlaing")], news_query='"Min Aung Hlaing"',
    ),
    "prayut-chan-o-cha": LeaderSpec(
        slug="prayut-chan-o-cha", name="Prayut Chan-o-cha", country="Thailand",
        region="Southeast Asia", continent="Asia",
        political_affiliation="United Thai Nation Party", current=1, office="Prime Minister",
        wikipedia=[("en", "Prayut Chan-o-cha")], news_query='"Prayut Chan-o-cha"',
    ),

    # --- International Organizations ---
    "antonio-guterres": LeaderSpec(
        slug="antonio-guterres", name="António Guterres", country="United Nations",
        region="Global", continent="Global",
        political_affiliation="Independent", current=1, office="Secretary-General",
        wikipedia=[("en", "António Guterres")], news_query='"Antonio Guterres"',
    ),
    "jens-stoltenberg": LeaderSpec(
        slug="jens-stoltenberg", name="Jens Stoltenberg", country="NATO",
        region="Global", continent="Global",
        political_affiliation="Conservative Party", current=1, office="Secretary-General",
        wikipedia=[("en", "Jens Stoltenberg")], news_query='"Jens Stoltenberg"',
    ),
    "tedros-adhanom": LeaderSpec(
        slug="tedros-adhanom", name="Tedros Adhanom", country="World Health Organization",
        region="Global", continent="Global",
        political_affiliation="Independent", current=1, office="Director-General",
        wikipedia=[("en", "Tedros Adhanom")], news_query='"Tedros Adhanom"',
    ),
    "kristalina-georgieva": LeaderSpec(
        slug="kristalina-georgieva", name="Kristalina Georgieva", country="International Monetary Fund",
        region="Global", continent="Global",
        political_affiliation="Independent", current=1, office="Managing Director",
        wikipedia=[("en", "Kristalina Georgieva")], news_query='"Kristalina Georgieva"',
    ),
}

PILOT_SLUGS = [s for s, spec in ROSTER.items() if spec.pilot]
