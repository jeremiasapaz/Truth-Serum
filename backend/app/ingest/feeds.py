"""Curated direct RSS feeds for newspapers, magazines and TV broadcasters.

Google News / Bing give per-query breadth across thousands of outlets; these
direct feeds add first-party corroboration from major publishers and TV channels.
Items are filtered to those mentioning the leader's name terms. Feeds are grouped
so a leader can pull global + region-relevant outlets.
"""

from __future__ import annotations

# (source_name, feed_url)
GLOBAL_FEEDS: list[tuple[str, str]] = [
    ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Reuters World", "https://news.google.com/rss/search?q=when:7d%20site:reuters.com&hl=en-US&gl=US&ceid=US:en"),
    ("The Guardian", "https://www.theguardian.com/world/rss"),
    ("NPR World", "https://feeds.npr.org/1004/rss.xml"),
    ("Deutsche Welle", "https://rss.dw.com/rdf/rss-en-world"),
    ("France 24", "https://www.france24.com/en/rss"),
    ("CNN World", "http://rss.cnn.com/rss/edition_world.rss"),
    ("Sky News", "https://feeds.skynews.com/feeds/rss/world.xml"),
]

REGION_FEEDS: dict[str, list[tuple[str, str]]] = {
    "South America": [
        ("G1 (Globo)", "https://g1.globo.com/rss/g1/politica/"),
        ("Folha - Poder", "https://feeds.folha.uol.com.br/poder/rss091.xml"),
        ("Folha - Em cima da hora", "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml"),
        ("Agência Brasil", "https://agenciabrasil.ebc.com.br/rss.xml"),
        ("Agência Pública", "https://apublica.org/feed/"),
        ("O Globo - Política", "https://oglobo.globo.com/rss/oglobo/politica"),
        ("Valor Econômico - Política", "https://valor.globo.com/rss/valor/politica/"),
        ("Estadão", "https://www.estadao.com.br/arc/outboundfeeds/rss/?outputType=xml"),
        ("Veja", "https://veja.abril.com.br/feed/"),
        ("Exame", "https://exame.com/feed/"),
        ("CartaCapital", "https://www.cartacapital.com.br/feed/"),
        ("ISTOÉ", "https://istoe.com.br/feed/"),
        ("CNN Brasil", "https://www.cnnbrasil.com.br/feed/"),
        ("Poder360", "https://www.poder360.com.br/feed/"),
        ("Metrópoles", "https://www.metropoles.com/feed"),
        ("Jovem Pan", "https://jovempan.com.br/feed"),
        ("Brasil de Fato", "https://www.brasildefato.com.br/feed"),
    ],
    "Europe": [
        ("The Irish Times", "https://www.irishtimes.com/cmlink/news-1.1319192"),
        ("RTÉ", "https://www.rte.ie/feeds/rss/?index=/news/"),
        ("Euronews", "https://www.euronews.com/rss"),
    ],
    "Middle East": [
        ("The Times of Israel", "https://www.timesofisrael.com/feed/"),
        ("Haaretz", "https://www.haaretz.com/srv/htz---all-news"),
    ],
    "Asia": [
        ("South China Morning Post", "https://www.scmp.com/rss/91/feed"),
        ("The Japan Times", "https://www.japantimes.co.jp/feed/"),
    ],
    "North America": [
        ("PBS NewsHour", "https://www.pbs.org/newshour/feeds/rss/politics"),
        ("Politico", "https://rss.politico.com/politics-news.xml"),
    ],
}


def feeds_for(continent: str) -> list[tuple[str, str]]:
    return GLOBAL_FEEDS + REGION_FEEDS.get(continent, [])
