# PharmaWatch

**Pakistan's first agentic AI consumer-protection system for the pharmaceutical sector.**

A user reports being overcharged at a pharmacy; the agent autonomously investigates — verifies the price against DRAP's official MRP, finds cheaper generic alternatives, cross-checks counterfeit/spurious medicine alerts, pulls the pharmacy's prior enforcement history, anonymously logs the report to a real-time community heatmap, and generates a pre-filled formal complaint letter to DRAP.

Built for **InnoCollab Hackathon 2026**.

---

## Stack

| Layer    | Tech |
|----------|------|
| Backend  | FastAPI (Python 3.11+), 3-tier modular monolith |
| LLM      | Gemini 2.5 Flash (agent loop) + Gemini 2.5 Pro (synthesis) — `google-generativeai` SDK |
| Frontend | React + Vite + Tailwind CSS |
| Data     | SQLite (DRAP "Golden Source") + Firebase Firestore (community reports, real-time heatmap) |
| Maps     | Google Maps JavaScript API |
| PDF      | ReportLab (server-side) |

See [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) for the full build spec, schemas, and 3-day plan.

---

## Repository Layout

```
PharmaWatch/
├── PROJECT_PLAN.md           # build spec, schemas, demo script
├── PharmaWatch_SRS_v2.pdf    # original Software Requirements Spec
├── backend/                  # FastAPI agent server
│   ├── app/
│   │   ├── api/              # Tier 1 — routes + Pydantic schemas
│   │   ├── agent/            # Tier 2 — Gemini orchestrator + tool registry
│   │   ├── services/         # Tier 2 — domain logic
│   │   ├── data/             # Tier 3 — SQLite + Firebase + external clients
│   │   ├── normalization/    # name matching, fuzzy lookup
│   │   └── core/             # logging, exceptions
│   ├── scripts/              # one-shot CLIs (DRAP scraper, seeders)
│   └── tests/
└── frontend/                 # (Day 1) React + Tailwind app
```

---

## Backend — Quick Start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Fill in: GEMINI_API_KEY, FIREBASE_PROJECT_ID, GOOGLE_MAPS_API_KEY
# Place Firebase service-account JSON at backend/firebase-credentials.json

# Initialize the local SQLite "Golden Source"
python scripts/scrape_drap.py --init-only

# Run the API
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

---

## Required API Keys

1. **Gemini** — free tier: https://aistudio.google.com/app/apikey
2. **Firebase** — create project + enable Firestore: https://console.firebase.google.com
   Generate a service account: *Project Settings → Service Accounts → Generate new private key* → save as `backend/firebase-credentials.json` (gitignored)
3. **Google Maps** — enable Places API + Maps JavaScript API: https://console.cloud.google.com/google/maps-apis

---

## Git Workflow

We follow **Git Flow**:

- `main` — production-quality, demo-ready
- `develop` — integration branch
- `feature/<short-name>` — branched from `develop`, merged via PR

Every commit and PR description includes:

```
Co-authored-by: Sultan Qureshi <sultanqureshi111@outlook.com>
```

---

## Team

- **Fozan Javaid** — full-stack
- **Sultan Qureshi** — full-stack — [sultanqureshi111@outlook.com](mailto:sultanqureshi111@outlook.com)

---

## Data Freshness

The local `drap.sqlite` is refreshed by `scripts/scrape_drap.py`. For production, deploy as a nightly cron:

```cron
0 2 * * *  /usr/bin/python /app/backend/scripts/scrape_drap.py
```

The UI surfaces `last_scraped_at` so users can see the freshness of the Golden Source.
