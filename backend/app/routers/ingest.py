from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..ingest.pipeline import ingest_leader
from ..ingest.roster import ROSTER

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.get("/roster")
def roster():
    return {
        "llm_enabled": get_settings().llm_enabled,
        "leaders": [
            {
                "slug": s, "name": spec.name, "country": spec.country,
                "office": spec.office, "current": spec.current, "pilot": spec.pilot,
            }
            for s, spec in ROSTER.items()
        ],
    }


@router.post("/leader/{slug}")
async def ingest(slug: str, use_news: bool = True, db: Session = Depends(get_db)):
    spec = ROSTER.get(slug)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Unknown slug. Known: {', '.join(ROSTER)}")
    if not get_settings().llm_enabled:
        raise HTTPException(
            status_code=400,
            detail="LLM_API_KEY not set. Ingestion needs an LLM to classify real evidence.",
        )
    return await ingest_leader(db, spec, use_news=use_news)


@router.post("/all")
async def ingest_all(db: Session = Depends(get_db)):
    """Ingest all leaders - useful for manual data population."""
    if not get_settings().llm_enabled:
        raise HTTPException(
            status_code=400,
            detail="LLM_API_KEY not set. Ingestion needs an LLM to classify real evidence.",
        )
    
    results = []
    for slug, spec in ROSTER.items():
        try:
            result = await ingest_leader(db, spec, use_news=True)
            results.append({"slug": slug, "name": spec.name, "status": "success", "result": result})
        except Exception as e:
            results.append({"slug": slug, "name": spec.name, "status": "failed", "error": str(e)})
    
    return {"total": len(results), "success": sum(1 for r in results if r["status"] == "success"), "results": results}
