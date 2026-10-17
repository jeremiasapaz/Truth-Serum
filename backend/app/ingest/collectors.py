"""Evidence collectors. Each returns real documents tied to real URLs.

Availability depends on the network: Wikipedia and the Brazilian gov APIs work
even behind a TLS-intercepting proxy (with VERIFY_SSL=false). GDELT is often
firewall-blocked on corporate networks but works from open networks. News
collectors require free API keys.
"""

from __future__ import annotations

import html
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

from ..config import get_settings
from ..constants import resolve_source
from .base import RawDoc, http_client


# ---------------------------------------------------------------------------
# Wikipedia — public, cited biographies (primary source here)
# ---------------------------------------------------------------------------
def collect_wikipedia(title: str, lang: str = "en") -> list[RawDoc]:
    """Fetch the full plain-text article for `title` as a single RawDoc."""
    base = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "redirects": "1",
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }
    with http_client() as client:
        r = client.get(base, params=params)
        r.raise_for_status()
        data = r.json()
    pages = data.get("query", {}).get("pages", [])
    docs: list[RawDoc] = []
    for page in pages:
        if page.get("missing"):
            continue
        extract = page.get("extract", "").strip()
        if not extract:
            continue
        canonical = page.get("title", title).replace(" ", "_")
        name, rating = resolve_source(f"{lang}.wikipedia.org")
        docs.append(
            RawDoc(
                title=page.get("title", title),
                url=f"https://{lang}.wikipedia.org/wiki/{canonical}",
                text=extract,
                source_name=name,
                source_rating=rating,
                published_at=None,
                kind="document",
                meta={"lang": lang},
            )
        )
    return docs


# ---------------------------------------------------------------------------
# GDELT 2.0 DOC API — global news (no key). Blocked on some networks.
# ---------------------------------------------------------------------------
def collect_gdelt(query: str, timespan: str = "12m", max_records: int = 40) -> list[RawDoc]:
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": str(max_records),
        "timespan": timespan,
        "format": "json",
        "sort": "datedesc",
    }
    try:
        with http_client(timeout=25.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001 - blocked/unreachable -> skip
        print(f"[gdelt] skipped: {type(exc).__name__}: {str(exc)[:80]}")
        return []

    docs: list[RawDoc] = []
    for a in data.get("articles", []):
        name, rating = resolve_source(a.get("domain", ""))
        docs.append(
            RawDoc(
                title=a.get("title", "").strip(),
                url=a.get("url", ""),
                text=a.get("title", "").strip(),
                source_name=name,
                source_rating=rating,
                published_at=_parse_gdelt_date(a.get("seendate")),
                kind="article",
                meta={"domain": a.get("domain"), "language": a.get("language")},
            )
        )
    return [d for d in docs if d.url and d.title]


def _parse_gdelt_date(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# GNews / NewsAPI — recent news (need free keys)
# ---------------------------------------------------------------------------
def collect_gnews(query: str, max_records: int = 30) -> list[RawDoc]:
    settings = get_settings()
    if not settings.gnews_api_key:
        return []
    url = "https://gnews.io/api/v4/search"
    params = {"q": query, "max": str(max_records), "apikey": settings.gnews_api_key, "lang": "en"}
    try:
        with http_client() as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[gnews] skipped: {type(exc).__name__}: {str(exc)[:80]}")
        return []
    docs = []
    for a in data.get("articles", []):
        domain = (a.get("source", {}) or {}).get("url", "")
        name, rating = resolve_source(_domain_of(domain))
        text = " ".join(filter(None, [a.get("title"), a.get("description")]))
        docs.append(
            RawDoc(
                title=a.get("title", ""), url=a.get("url", ""), text=text,
                source_name=name or a.get("source", {}).get("name", "News"),
                source_rating=rating,
                published_at=_parse_iso(a.get("publishedAt")),
                kind="article",
            )
        )
    return [d for d in docs if d.url and d.title]


def collect_newsapi(query: str, max_records: int = 30) -> list[RawDoc]:
    settings = get_settings()
    if not settings.newsapi_key:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "pageSize": str(max_records), "sortBy": "publishedAt", "language": "en"}
    try:
        with http_client() as client:
            r = client.get(url, params=params, headers={"X-Api-Key": settings.newsapi_key})
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[newsapi] skipped: {type(exc).__name__}: {str(exc)[:80]}")
        return []
    docs = []
    for a in data.get("articles", []):
        name, rating = resolve_source(_domain_of(a.get("url", "")))
        text = " ".join(filter(None, [a.get("title"), a.get("description")]))
        docs.append(
            RawDoc(
                title=a.get("title", ""), url=a.get("url", ""), text=text,
                source_name=name, source_rating=rating,
                published_at=_parse_iso(a.get("publishedAt")),
                kind="article",
            )
        )
    return [d for d in docs if d.url and d.title]


def _domain_of(url: str) -> str:
    if not url:
        return ""
    try:
        return urlparse(url).netloc
    except Exception:  # noqa: BLE001
        return ""


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Generic RSS/Atom parsing helpers
# ---------------------------------------------------------------------------
def _strip_html(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def _tag(el) -> str:
    """Local tag name, ignoring XML namespace."""
    return el.tag.rsplit("}", 1)[-1].lower()


def _parse_rfc822(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return parsedate_to_datetime(s)
    except (TypeError, ValueError):
        return None


def _parse_rss_items(xml_bytes: bytes) -> list[dict]:
    """Parse RSS 2.0 / Atom into a list of {title, link, desc, pubdate, source, source_url}."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    items: list[dict] = []
    for node in root.iter():
        if _tag(node) not in ("item", "entry"):
            continue
        rec = {"title": "", "link": "", "desc": "", "pubdate": None,
               "source": "", "source_url": ""}
        for child in node:
            t = _tag(child)
            if t == "title":
                rec["title"] = (child.text or "").strip()
            elif t == "link":
                rec["link"] = (child.text or "").strip() or child.attrib.get("href", "")
            elif t in ("description", "summary", "content"):
                rec["desc"] = _strip_html(child.text or "")
            elif t in ("pubdate", "published", "updated"):
                rec["pubdate"] = _parse_rfc822(child.text) or _parse_iso(child.text)
            elif t == "source":
                rec["source"] = (child.text or "").strip()
                rec["source_url"] = child.attrib.get("url", "")
        if rec["title"] and rec["link"]:
            items.append(rec)
    return items


def _rss_to_docs(items: list[dict], fallback_source: str = "") -> list[RawDoc]:
    docs: list[RawDoc] = []
    for it in items:
        # Prefer the explicit <source> (Google News), else the link domain.
        dom = _domain_of(it.get("source_url") or it["link"])
        name, rating = resolve_source(dom)
        if name in ("Unknown source",) and it.get("source"):
            name = it["source"]
        if name in ("Unknown source",) and fallback_source:
            name = fallback_source
        # Google News titles are usually "Headline - Outlet"; trim the outlet.
        title = re.sub(r"\s+-\s+[^-]+$", "", it["title"]).strip() or it["title"]
        text = " ".join(filter(None, [title, it.get("desc", "")]))[:1200]
        docs.append(
            RawDoc(
                title=title, url=it["link"], text=text,
                source_name=name, source_rating=rating,
                published_at=it.get("pubdate"), kind="article",
                meta={"domain": dom},
            )
        )
    return docs


# ---------------------------------------------------------------------------
# Google News RSS — keyless aggregator spanning thousands of outlets, per locale
# ---------------------------------------------------------------------------
def collect_google_news(query: str, locales: list[tuple[str, str]] | None = None) -> list[RawDoc]:
    """locales: list of (hl, gl) e.g. [("en-US","US"), ("pt-BR","BR")]."""
    locales = locales or [("en-US", "US")]
    settings = get_settings()
    out: list[RawDoc] = []
    for hl, gl in locales:
        ceid = f"{gl}:{hl.split('-')[0]}"
        url = "https://news.google.com/rss/search"
        params = {"q": query, "hl": hl, "gl": gl, "ceid": ceid}
        try:
            with http_client() as client:
                r = client.get(url, params=params)
                r.raise_for_status()
            docs = _rss_to_docs(_parse_rss_items(r.content), fallback_source="Google News")
            out += docs[: settings.max_items_per_source]
        except Exception as exc:  # noqa: BLE001
            print(f"[google-news {hl}] skipped: {type(exc).__name__}: {str(exc)[:70]}")
    return out


# ---------------------------------------------------------------------------
# Bing News RSS — keyless aggregator
# ---------------------------------------------------------------------------
def collect_bing_news(query: str) -> list[RawDoc]:
    settings = get_settings()
    url = "https://www.bing.com/news/search"
    params = {"q": query, "format": "rss"}
    try:
        with http_client() as client:
            r = client.get(url, params=params)
            r.raise_for_status()
        docs = _rss_to_docs(_parse_rss_items(r.content), fallback_source="Bing News")
        return docs[: settings.max_items_per_source]
    except Exception as exc:  # noqa: BLE001
        print(f"[bing-news] skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return []


# ---------------------------------------------------------------------------
# Generic outlet RSS feeds (newspapers / magazines / TV broadcasters)
# ---------------------------------------------------------------------------
def collect_rss_feeds(feeds: list[tuple[str, str]], query_terms: list[str]) -> list[RawDoc]:
    """feeds: [(source_name, feed_url)]. Filtered to items mentioning query_terms."""
    settings = get_settings()
    terms = [t.lower() for t in query_terms if t]
    out: list[RawDoc] = []
    for source_name, feed_url in feeds:
        try:
            with http_client(timeout=20.0) as client:
                r = client.get(feed_url)
                r.raise_for_status()
            docs = _rss_to_docs(_parse_rss_items(r.content), fallback_source=source_name)
        except Exception as exc:  # noqa: BLE001
            print(f"[rss {source_name}] skipped: {type(exc).__name__}: {str(exc)[:60]}")
            continue
        if terms:
            docs = [d for d in docs if any(t in d.text.lower() for t in terms)]
        out += docs[: settings.max_items_per_source]
    return out


# ---------------------------------------------------------------------------
# Keyed aggregators (each spans many outlets) — optional
# ---------------------------------------------------------------------------
def collect_newsdata(query: str) -> list[RawDoc]:
    settings = get_settings()
    if not settings.newsdata_api_key:
        return []
    url = "https://newsdata.io/api/1/news"
    params = {"apikey": settings.newsdata_api_key, "q": query, "language": "en"}
    try:
        with http_client() as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[newsdata] skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return []
    docs = []
    for a in data.get("results", []):
        name, rating = resolve_source(_domain_of(a.get("link", "")))
        text = " ".join(filter(None, [a.get("title"), a.get("description")]))
        docs.append(RawDoc(
            title=a.get("title", ""), url=a.get("link", ""), text=text,
            source_name=name, source_rating=rating,
            published_at=_parse_iso(a.get("pubDate")), kind="article",
        ))
    return [d for d in docs if d.url and d.title][: settings.max_items_per_source]


def collect_mediastack(query: str) -> list[RawDoc]:
    settings = get_settings()
    if not settings.mediastack_api_key:
        return []
    url = "http://api.mediastack.com/v1/news"
    params = {"access_key": settings.mediastack_api_key, "keywords": query, "languages": "en"}
    try:
        with http_client() as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[mediastack] skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return []
    docs = []
    for a in data.get("data", []):
        name, rating = resolve_source(_domain_of(a.get("url", "")))
        text = " ".join(filter(None, [a.get("title"), a.get("description")]))
        docs.append(RawDoc(
            title=a.get("title", ""), url=a.get("url", ""), text=text,
            source_name=name, source_rating=rating,
            published_at=_parse_iso(a.get("published_at")), kind="article",
        ))
    return [d for d in docs if d.url and d.title][: settings.max_items_per_source]


def collect_currents(query: str) -> list[RawDoc]:
    settings = get_settings()
    if not settings.currents_api_key:
        return []
    url = "https://api.currentsapi.services/v1/search"
    params = {"apiKey": settings.currents_api_key, "keywords": query, "language": "en"}
    try:
        with http_client() as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[currents] skipped: {type(exc).__name__}: {str(exc)[:70]}")
        return []
    docs = []
    for a in data.get("news", []):
        name, rating = resolve_source(_domain_of(a.get("url", "")))
        text = " ".join(filter(None, [a.get("title"), a.get("description")]))
        docs.append(RawDoc(
            title=a.get("title", ""), url=a.get("url", ""), text=text,
            source_name=name, source_rating=rating,
            published_at=_parse_iso(a.get("published")), kind="article",
        ))
    return [d for d in docs if d.url and d.title][: settings.max_items_per_source]
