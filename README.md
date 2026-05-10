# PharmaWatch

**Pakistan's first agentic AI consumer-protection system for the pharmaceutical sector.**

A user reports being overcharged at a pharmacy. The agent autonomously plans an investigation, verifies the price against DRAP's official MRP, finds cheaper generic alternatives, cross-checks counterfeit/spurious medicine alerts, **pulls the pharmacy's prior enforcement history with notice references and penalty amounts**, anonymously logs the report to a real-time community heatmap, and generates a pre-filled formal complaint letter to DRAP — all observable as a live tool-call trace.

Built for **InnoCollab Hackathon 2026** (Google for Developers · Telenor 4G · MoITT · Innovista).

---

## What makes this an actual agent

Most "AI" hackathon projects follow a fixed pipeline: user input → LLM → output. PharmaWatch is architecturally different. The agent **autonomously decides** which of its 9 tools to call, in what order, and whether to retry — based on what each tool returns. Every tool call streams to the frontend over Server-Sent Events so judges can watch the Plan → Execute → Evaluate → Loop → Conclude cycle happen live.

```
9 tools registered:
  drap_price_lookup           generic_alternatives          spurious_alert_check
  drap_enforcement_lookup     log_community_report          get_pharmacy_reports
  generate_complaint_letter   generate_collective_dossier   web_search_fallback
```

---

## Stack

| Layer    | Tech |
|----------|------|
| Backend  | FastAPI (Python 3.11+), 3-tier modular monolith |
| LLM      | Gemini 2.5 Flash (agent loop) — `google-genai` SDK |
| Frontend | React 18 + Vite + Tailwind CSS |
| Maps     | Google Maps JavaScript API (`@vis.gl/react-google-maps`) |
| Data     | SQLite (DRAP "Golden Source") + Firebase Firestore (community reports, real-time heatmap) |
| PDFs     | ReportLab (server-side) |
| Tests    | pytest with in-memory SQLite + fake Firestore + scripted FakeChat for the agent loop |

See [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) for the full build spec, schemas, and demo script.

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
│   │   ├── services/         # Tier 2 — domain logic (PDF, builders, pattern detection)
│   │   ├── data/             # Tier 3 — SQLite + Firebase + external clients
│   │   ├── normalization/    # name matching, slug generation
│   │   └── core/             # logging, exceptions
│   ├── scripts/              # one-shot CLIs (DRAP scraper, seed_drap)
│   ├── data_store/seed/      # JSON fixtures for the demo
│   └── tests/                # 26 tests, ruff-clean
└── frontend/                 # React + Tailwind app
    ├── src/
    │   ├── pages/            # HomePage (heatmap), InvestigatePage (form + trace + report)
    │   ├── components/       # Heatmap, AgentTracePanel, InvestigationReport, ReportForm, ...
    │   ├── hooks/            # useAgentStream (SSE), useHeatmap (Firestore live), useDataFreshness
    │   └── lib/              # api.js, firebase.js, format helpers
    └── public/
```

---

## Quick Start

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Add GEMINI_API_KEY (free at https://aistudio.google.com/app/apikey)
# Optional: FIREBASE_* (community heatmap)

# Seed the local DRAP "Golden Source" with demo data
python scripts/seed_drap.py

# Run the API
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health` returns the data freshness per scraped table.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Optional: VITE_GOOGLE_MAPS_API_KEY (real heatmap), VITE_FIREBASE_* (live updates)
npm run dev
# → http://localhost:5173
```

The Vite dev proxy forwards `/agent`, `/reports`, `/complaint`, `/dossier`, `/health` to the FastAPI server on `:8000` — no CORS gymnastics.

---

## The Demo Flow

1. **Open** `http://localhost:5173` — Pakistan heatmap, Saddar/Karachi has a red dot for *City Pharmacy* (3 verified violations on file).
2. **Click "Investigate"** → form prefilled with the canonical demo example: *"I was charged Rs. 1,200 for Ceftum 500mg at City Pharmacy, Saddar, Karachi."*
3. **Hit Investigate** → trace panel streams the Plan→Execute→Evaluate cycle live as the agent fires:
   - `drap_price_lookup` → MRP **Rs. 640** ✓
   - `spurious_alert_check` → no current alert ✓
   - `generic_alternatives` → 3 cheaper brands found
   - `drap_enforcement_lookup` → **3 prior violations, Rs. 250K in fines** ⚡
   - `log_community_report` → anonymous report logged
   - `get_pharmacy_reports` → classification updated
   - `generate_complaint_letter` → ready
4. **Investigation Report renders progressively**:
   - Overcharge: **Rs. 560 (87.5% above MRP)**
   - Cheapest alternative: **Cefim Rs. 390** (saves Rs. 810)
   - **Pharmacy enforcement history with clickable DRAP notice URLs** ← the demo killshot
5. **One click** → complaint letter PDF downloads.

---

## Required API Keys

| Service | Purpose | Free tier |
|---|---|---|
| [Gemini](https://aistudio.google.com/app/apikey) | Agent loop | Yes — generous |
| [Firebase](https://console.firebase.google.com) | Community reports, real-time heatmap | Yes — Spark plan |
| [Google Maps](https://console.cloud.google.com/google/maps-apis) | Heatmap visualization (Places + Maps JavaScript) | $200/month credit |

The frontend degrades gracefully when keys are missing: heatmap falls back to a sortable list, live updates disable cleanly.

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

## Privacy & Honesty

- **Zero PII** stored. Community reports never collect name, phone, CNIC, email, or IP. The session hash is one-way (rate-limit only).
- **DRAP data is canonical.** The agent will never invent a price, registration number, or enforcement action. If a tool returns no result, it retries once with a reformulated query and then honestly reports "not found".
- **Real-time pharmacy inventory is not available.** No public API exists for Pakistani pharmacy stock. PharmaWatch verifies prices and surfaces alternatives — confirming a specific pharmacy has a generic in stock is Phase 2 (requires direct pharmacy partnerships).
- **Data freshness** is surfaced in the UI footer: *"DRAP data current as of …"*

---

## Team

- **Fozan Javaid** — full-stack
- **Sultan Qureshi** — full-stack — [sultanqureshi111@outlook.com](mailto:sultanqureshi111@outlook.com)

---

*Built with purpose. Powered by DRAP's public data. Anonymous by design.*
