"""
Batch ingestion script - processes 5 leaders per day.
This spreads LLM credit usage across the week.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.ingest.run import ingest_leader
from app.ingest.roster import ROSTER

# Get all leader slugs
ALL_SLUGS = list(ROSTER.keys())

# Split into batches of 5
BATCH_SIZE = 5
BATCHES = [ALL_SLUGS[i:i + BATCH_SIZE] for i in range(0, len(ALL_SLUGS), BATCH_SIZE)]

# Determine which batch to run based on day of week (0=Monday, 6=Sunday)
def get_batch_index():
    day_of_week = datetime.now().weekday()
    # Use modulo to cycle through batches
    return day_of_week % len(BATCHES)


async def batch_ingest():
    """Ingest the current day's batch of leaders."""
    batch_index = get_batch_index()
    current_batch = BATCHES[batch_index]
    
    db = SessionLocal()
    try:
        print(f"Starting batch {batch_index + 1}/{len(BATCHES)} for {len(current_batch)} leaders...")
        print(f"Leaders to process: {current_batch}")
        
        for slug in current_batch:
            spec = ROSTER.get(slug)
            if not spec:
                print(f"  SKIP {slug} - not found in roster")
                continue
            
            print(f"Processing {spec.name}...")
            try:
                await ingest_leader(db, spec, use_news=True)
                print(f"  OK {spec.name} updated")
            except Exception as e:
                print(f"  FAIL {spec.name} failed: {e}")
        
        print(f"Batch {batch_index + 1} complete!")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(batch_ingest())
