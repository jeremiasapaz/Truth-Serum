"""Shared types and HTTP helpers for evidence ingestion collectors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import httpx

from ..config import get_settings


@dataclass
class RawDoc:
    """A raw document retrieved from a public source, tied to a real URL.

    `text` is the content the LLM will read to extract/classify evidence.
    Long documents (e.g. a Wikipedia article) carry the whole body; short ones
    (e.g. a news item) carry the title + any snippet.
    """

    title: str
    url: str
    text: str
    source_name: str
    source_rating: float
    published_at: datetime | None = None
    kind: str = "document"  # "document" (multi-evidence) or "article" (0-1)
    meta: dict = field(default_factory=dict)


def http_client(timeout: float = 30.0) -> httpx.Client:
    settings = get_settings()
    return httpx.Client(
        timeout=timeout,
        verify=settings.verify_ssl,
        follow_redirects=True,
        headers={"User-Agent": "leader-transparency-research/0.1 (public-evidence)"},
    )
