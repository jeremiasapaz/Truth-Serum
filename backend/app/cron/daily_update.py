"""
Daily scheduled update job.
Re-scores all leaders with current evidence.
Run this daily at 8 AM EST via cron.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.ingest.run import ingest_leader
from app.ingest.roster import ROSTER


async def daily_update():
    """Re-score all leaders with current evidence."""
    db = SessionLocal()
    try:
        print(f"Starting daily update for {len(ROSTER)} leaders...")
        
        for slug, spec in ROSTER.items():
            print(f"Processing {spec.name}...")
            try:
                # Ingest evidence for this leader
                # Note: This uses the configured LLM with fallback
                await ingest_leader(db, spec, use_news=True)
                print(f"  OK {spec.name} updated")
            except Exception as e:
                print(f"  FAIL {spec.name} failed: {e}")
        
        print("Daily update complete!")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(daily_update())
