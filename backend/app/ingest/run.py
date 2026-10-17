"""CLI: ingest real evidence for roster leaders.

Examples:
    python -m app.ingest.run --pilot
    python -m app.ingest.run lula jair-bolsonaro
    python -m app.ingest.run --all --no-news
"""

from __future__ import annotations

import argparse
import asyncio

from ..config import get_settings
from ..database import Base, SessionLocal, engine
from .pipeline import ingest_leader
from .roster import PILOT_SLUGS, ROSTER


async def _run(slugs: list[str], use_news: bool) -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    if not settings.llm_enabled:
        print("ERROR: LLM_API_KEY is not set. Ingestion needs an LLM to classify")
        print("real evidence responsibly. Add it to backend/.env (see .env.example).")
        return

    db = SessionLocal()
    try:
        for slug in slugs:
            spec = ROSTER.get(slug)
            if not spec:
                print(f"- unknown slug: {slug} (known: {', '.join(ROSTER)})")
                continue
            print(f"\n=== Ingesting {spec.name} ({slug}) ===")
            summary = await ingest_leader(db, spec, use_news=use_news)
            print(summary)
    finally:
        db.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Ingest real evidence for leaders.")
    p.add_argument("slugs", nargs="*", help="roster slugs to ingest")
    p.add_argument("--pilot", action="store_true", help="ingest the pilot set")
    p.add_argument("--all", action="store_true", help="ingest the full roster")
    p.add_argument("--no-news", action="store_true", help="Wikipedia only (skip news/GDELT)")
    args = p.parse_args()

    if args.all:
        slugs = list(ROSTER)
    elif args.pilot:
        slugs = PILOT_SLUGS
    else:
        slugs = args.slugs or PILOT_SLUGS

    asyncio.run(_run(slugs, use_news=not args.no_news))


if __name__ == "__main__":
    main()
