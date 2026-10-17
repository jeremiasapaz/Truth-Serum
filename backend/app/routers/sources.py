"""Public source registry — lists every feed/API the platform taps, with links,
so anyone can verify the sources are real and inspect the methodology."""

from fastapi import APIRouter

from ..config import get_settings
from ..constants import DOMAIN_RATINGS, STATE_MEDIA_DOMAINS
from ..country.catalog import INDICATORS
from ..ingest.feeds import GLOBAL_FEEDS, REGION_FEEDS

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("")
def sources():
    s = get_settings()

    evidence_collectors = [
        {"name": "Wikipedia", "kind": "Encyclopedia (cited)", "keyless": True, "active": True,
         "url": "https://en.wikipedia.org", "note": "Primary biographical source; LLM extracts only text-supported claims."},
        {"name": "Google News RSS", "kind": "News aggregator", "keyless": True, "active": True,
         "url": "https://news.google.com/rss", "note": "Queried per country + language (local + foreign press)."},
        {"name": "Bing News RSS", "kind": "News aggregator", "keyless": True, "active": True,
         "url": "https://www.bing.com/news", "note": "Keyless secondary aggregator."},
        {"name": "Direct outlet / TV RSS", "kind": "First-party feeds", "keyless": True, "active": True,
         "url": "", "note": "Curated publisher feeds (see News feeds list)."},
        {"name": "GDELT 2.0", "kind": "Global news index", "keyless": True,
         "active": False, "url": "https://www.gdeltproject.org",
         "note": "Supported, but blocked on some corporate networks."},
        {"name": "GNews", "kind": "News aggregator (keyed)", "keyless": False,
         "active": bool(s.gnews_api_key), "url": "https://gnews.io", "note": "Optional free key."},
        {"name": "NewsAPI", "kind": "News aggregator (keyed)", "keyless": False,
         "active": bool(s.newsapi_key), "url": "https://newsapi.org", "note": "Optional free key."},
        {"name": "NewsData", "kind": "News aggregator (keyed)", "keyless": False,
         "active": bool(s.newsdata_api_key), "url": "https://newsdata.io", "note": "Optional free key."},
        {"name": "Mediastack", "kind": "News aggregator (keyed)", "keyless": False,
         "active": bool(s.mediastack_api_key), "url": "https://mediastack.com", "note": "Optional free key."},
        {"name": "Currents", "kind": "News aggregator (keyed)", "keyless": False,
         "active": bool(s.currents_api_key), "url": "https://currentsapi.services", "note": "Optional free key."},
    ]

    def feed_rows(feeds, region):
        rows = []
        for name, url in feeds:
            dom = _domain(url)
            rating = DOMAIN_RATINGS.get(dom, (name, 0.5))[1]
            rows.append({"name": name, "url": url, "region": region, "rating": rating,
                         "state_media": dom in STATE_MEDIA_DOMAINS})
        return rows

    news_feeds = feed_rows(GLOBAL_FEEDS, "Global")
    for region, feeds in REGION_FEEDS.items():
        news_feeds += feed_rows(feeds, region)

    # Country data providers
    def ind_rows(src):
        out = []
        for i in INDICATORS:
            if i.source != src:
                continue
            if src == "worldbank":
                url = f"https://data.worldbank.org/indicator/{i.code.split('|')[0]}"
            elif src == "owid":
                url = f"https://ourworldindata.org/grapher/{i.provider_code}"
            elif src == "eurostat":
                url = f"https://ec.europa.eu/eurostat/databrowser/view/{i.provider_code}/default/table?lang=en"
            else:
                url = ""
            out.append({"code": i.code, "name": i.name, "category": i.category,
                        "unit": i.unit, "dataset": i.dataset, "url": url})
        return out

    pluggable = [
        {"code": i.code, "name": i.name, "category": i.category, "intended_source": i.pluggable_source}
        for i in INDICATORS if i.source is None
    ]

    return {
        "principle": "Every score traces to a real, cited source. This page lists them all so you can verify.",
        "llm": {
            "provider_base_url": s.llm_base_url,
            "model": s.llm_model if s.llm_enabled else None,
            "enabled": s.llm_enabled,
            "note": "Classifies/scores only text from the real sources below; never invents facts.",
        },
        "evidence_collectors": evidence_collectors,
        "news_feeds": sorted(news_feeds, key=lambda r: (r["region"], r["name"])),
        "country_data": {
            "World Bank Open Data": ind_rows("worldbank"),
            "Our World in Data": ind_rows("owid"),
            "Eurostat": ind_rows("eurostat"),
        },
        "pluggable_indicators": pluggable,
        "source_ratings": sorted(
            [{"domain": d, "name": n, "rating": r, "state_media": d in STATE_MEDIA_DOMAINS}
             for d, (n, r) in DOMAIN_RATINGS.items()],
            key=lambda x: -x["rating"],
        ),
    }


def _domain(url: str) -> str:
    if not url:
        return ""
    from urllib.parse import urlparse
    return urlparse(url).netloc.replace("www.", "")
