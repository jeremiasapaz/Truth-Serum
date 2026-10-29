from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .country.seed import seed_administrations
from .database import Base, SessionLocal, engine
from .ingest.seed_leaders import ensure_real_leaders
from .routers import compare, country, evidence, ingest, leaders, scoring, sources
from .routers.transcripts import router as transcripts_router
from .routers.financial import router as financial_router
from .routers.brazil import router as brazil_router
from .routers.representation import router as representation_router
from .routers.proposals import router as proposals_router
from .routers.expenses import router as expenses_router
from .seed_financial import seed_financial_data

app = FastAPI(
    title="Truth Serum",
    description=(
        "Evaluates documented public evidence and source weighting to assign "
        "transparency scores. Does not determine legal guilt."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leaders.router)
app.include_router(evidence.router)
app.include_router(compare.router)
app.include_router(scoring.router)
app.include_router(ingest.router)
app.include_router(country.router)
app.include_router(sources.router)
app.include_router(transcripts_router)
app.include_router(financial_router)
app.include_router(brazil_router)
app.include_router(representation_router)
app.include_router(proposals_router)
app.include_router(expenses_router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_real_leaders(db)   # real roster (replaces fictional demo leaders)
        seed_administrations(db)
        seed_financial_data()    # seed financial data for leaders
    finally:
        db.close()


@app.get("/api/health")
def health():
    settings = get_settings()
    return {"status": "ok", "llm_enabled": settings.llm_enabled}


# --- Serve the static frontend -------------------------------------------
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR / "static")),
        name="static",
    )

    @app.get("/")
    def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
