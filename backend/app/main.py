from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers import compare, evidence, ingest, leaders, scoring
from .seed import seed_if_empty

app = FastAPI(
    title="Leader Transparency Scoring Platform",
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


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
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
