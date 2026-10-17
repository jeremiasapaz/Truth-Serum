"""Evidence collectors. Each returns real documents tied to real URLs.

Availability depends on the network: Wikipedia and the Brazilian gov APIs work
even behind a TLS-intercepting proxy (with VERIFY_SSL=false). GDELT is often
firewall-blocked on corporate networks but works from open networks. News
collectors require free API keys.
"""

from __future__ import annotations

from datetime import UTC, datetime

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
        from urllib.parse import urlparse

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
