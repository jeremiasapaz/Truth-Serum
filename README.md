# Leader Transparency Scoring Platform

Evaluates **documented public evidence** and **source weighting** to assign
transparency scores to political leaders across 10 categories. The AI does
**not** determine legal guilt — it scores the weight and quality of public
evidence, and every score is reproducible from the stored evidence.

> ⚠️ The seeded leaders and evidence are **fictional demonstration data**. Replace
> them with vetted, sourced records before any real use.

## Architecture

- **Backend:** FastAPI + SQLAlchemy (SQLite by default).
  - `app/scoring.py` — deterministic Trust & Confidence engine (the reproducible baseline).
  - `app/llm.py` — real LLM scoring (OpenAI-compatible) with graceful fallback to the engine.
  - `app/constants.py` — categories, evidence-classification weights, source ratings, trust weights.
  - `app/routers/` — leaders (filters/sorts), evidence (audit), compare (+trend history), scoring (+methodology).
- **Frontend:** single-page app served by FastAPI (vanilla JS + Chart.js via CDN — no Node build step).
  - Dashboard with advanced filters/sorts, leader detail drawer, evidence audit modal.
  - Compare view: radar, bar, heatmap, and trend charts (up to 10 leaders).
  - Methodology view exposing the full scoring formula.

## Scoring methodology

Final **confidence** = 40% source quality + 25% source quantity + 20% recency +
15% evidence consistency. Category **score** is +1 / 0 / −1 based on the
source- and reliability-weighted net polarity of evidence. Controversial
categories discount single-source, disputed, and unverified claims.

## Run

```bash
cd backend
python -m venv venv
./venv/Scripts/pip.exe install -r requirements.txt      # Windows (Git Bash)
# source venv/bin/activate && pip install -r requirements.txt   # macOS/Linux

./venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8077
```

Open http://127.0.0.1:8077

The SQLite DB is auto-created and seeded on first startup (`transparency.db`).
Delete that file to re-seed.

## Enable real LLM scoring

```bash
cp backend/.env.example backend/.env
# set LLM_API_KEY (and optionally LLM_BASE_URL / LLM_MODEL)
```

Restart the server. When a key is present, the "Re-run AI scoring (LLM)" button
in a leader's detail drawer scores each category with the model, honoring the
methodology prompt. Without a key, scoring falls back to the deterministic
engine so the platform always works.

## Key API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/leaders` | List + filter + sort leaders |
| GET | `/api/leaders/{id}` | Leader detail with category scores |
| GET | `/api/leaders/filters/options` | Available filter values |
| GET | `/api/evidence/leader/{id}` | Evidence for a leader |
| GET | `/api/evidence/{id}` | Single evidence record (audit view) |
| GET | `/api/compare?ids=1&ids=2` | Compare up to 10 leaders |
| GET | `/api/compare/trend/{id}` | Score history (trend chart) |
| POST | `/api/scoring/leader/{id}` | Re-run scoring (LLM or engine) |
| GET | `/api/scoring/methodology` | Full scoring formula & weights |
| GET | `/api/ingest/roster` | Real leaders available to ingest |
| POST | `/api/ingest/leader/{slug}` | Ingest real evidence + score a leader |

Interactive API docs: http://127.0.0.1:8077/docs

## Real-evidence ingestion

Retrieval-augmented pipeline (`app/ingest/`): collectors fetch **real documents
tied to real URLs**, an LLM extracts evidence **strictly grounded in the source
text** (category + classification + polarity), records are stored with source
rating/date/URL, then the leader is scored. The LLM never invents facts; if no
`LLM_API_KEY` is set, ingestion refuses to auto-tag real people.

**Sources (cross-checked across as many outlets as possible):**

- *Keyless, work out of the box:* Wikipedia, **Google News RSS** (per-country +
  per-language — local & foreign press/magazines across thousands of outlets),
  **Bing News RSS**, and direct outlet/TV RSS feeds (BBC, Al Jazeera, Reuters,
  The Guardian, France 24, DW, Sky, Folha, G1, Agência Brasil, RTÉ, Irish Times,
  SCMP, Japan Times, Times of Israel, Haaretz, PBS, Politico, …).
- *Keyless but often firewall-blocked on corporate networks:* GDELT.
- *Optional keyed aggregators (each spans many outlets):* GNews, NewsAPI,
  NewsData, Mediastack, Currents — add keys in `.env` to widen coverage.

Each source is rated (`DOMAIN_RATINGS`); state-controlled outlets are flagged and
down-weighted. The engine already rewards **independent-source corroboration**
(source quantity + consistency), so the same claim reported by many outlets
raises confidence, while single-source claims are discounted.

**Run ingestion** (needs `LLM_API_KEY`):

```bash
cd backend
python -m app.ingest.run --pilot              # Lula, Jair & Flavio Bolsonaro
python -m app.ingest.run lula --no-news       # Wikipedia only (fewer LLM calls)
python -m app.ingest.run --all                # full roster
```

Note on networks: GDELT/TV APIs are blocked on some corporate networks; set
`VERIFY_SSL=false` behind a TLS-intercepting proxy.
