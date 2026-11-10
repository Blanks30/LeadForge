# LeadForge — Evidence-First Sales Intelligence for B2B SaaS

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-102%20Passing-brightgreen.svg)]()
[![Zero Hallucination](https://img.shields.io/badge/Epistemic-Zero%20Hallucination-success.svg)]()

> **LeadForge** transforms public-web research into grounded, explainable prospect intelligence and hyper-personalized cold outreach drafts for SDRs selling to Indian B2B SaaS and MSME verticals.

---

## Key Pillars

1. **Strict Epistemic Classification:** Every extracted claim is categorised as:
   - `FACT`: Direct verbatim quote backed by exact source URL and publication date. Verified by automated SubString match against raw page content.
   - `INFERENCE`: Logical deduction with transparent, step-by-step reasoning (`gemini_reasoning`).
   - `UNKNOWN`: Critical unobserved attributes explicitly recorded. The system **never** guesses or invents numbers.
2. **Transparent 100-Point Mathematical Rubric:**
   - **SMB Focus in India (35 pts):** Explicit MSME target, INR (₹) pricing, mobile/WhatsApp onboarding.
   - **SaaS Delivery Model (25 pts):** Cloud-hosted architecture, transparent tiered pricing.
   - **Growth & Market Signals (20 pts):** Recent product releases (< 12 mo), hiring or expansion signals.
   - **Evidence Quality (20 pts):** High ratio of verified facts to unknowns, multi-page crawl verification.
3. **Zero Auto-Send Guarantee:** LeadForge produces review drafts with strict citation markers (e.g. `[Ref: #3]`). No automated email dispatching libraries exist in the runtime; SDR review and 1-click clipboard copy is mandatory.
4. **Deterministic Fallback & Provenance Tracking:** Seamlessly operates offline or during API rate limits with deterministic fixtures and templates. Every outreach draft records whether it originated from `Gemini AI` or a `Deterministic Template`.

---

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                             Multi-Stage Research Pipeline                         │
├───────────────────┬────────────────────┬────────────────────┬─────────────────────┤
│ Stage 1           │ Stage 2            │ Stage 3            │ Stage 4             │
│ Web Scraper       │ Evidence Extractor │ Scoring Engine     │ Outreach Generator  │
├───────────────────┼────────────────────┼────────────────────┼─────────────────────┤
│ TinyFish API /    │ Gemini API /       │ Python 3.12 Engine │ Gemini API /        │
│ Mock Adapter      │ Mock Adapter       │ Deterministic      │ Templated Generator │
│ Crawls homepage,  │ Extracts quotes,   │ 100-point rubric   │ Drafts cold email   │
│ about, & pricing  │ categorizes facts, │ calculated in pure │ citing verified     │
│ pages into SQLite │ inferences & gaps  │ Python mathematics │ evidence items only │
└───────────────────┴────────────────────┴────────────────────┴─────────────────────┘
```

---

## Technology Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy (asyncio), aiosqlite (SQLite with WAL mode), Pydantic v2 Settings.
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React.
- **AI & Crawling:** Google Gemini API (`gemini-1.5-flash` / `gemini-2.0-flash`), TinyFish Public Web Scraping API.
- **Testing & Quality:** Pytest, pytest-asyncio, Ruff (linter & formatter).

---

## Quickstart Guide

### Prerequisites
- Python 3.12+
- Node.js 20+

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (if not already created)
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start backend development server
$env:PYTHONPATH="backend"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000/api`
- Interactive API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### 2. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm.cmd install

# Start frontend development server
npm.cmd run dev
```
- Web Application: `http://localhost:5173`

---

## Docker Deployment

Run the complete multi-container production stack with Docker Compose:

```powershell
docker-compose up --build -d
```

- Frontend App: `http://localhost:80`
- Backend API: `http://localhost:8000/api`
- Persistent Volume: SQLite data is stored in the `leadforge_sqlite_data` named volume at `/app/backend/data` to ensure data persists across container restarts.

---

## Configuration & Environment Variables

Create a `backend/.env` file (copied from `backend/.env.example`):

```bash
# Application Runtime Mode (development, staging, production)
ENVIRONMENT=development

# Offline Demonstration Mode (true = use grounded mock fixtures; false = use live APIs)
USE_MOCK_APIS=true

# Google Gemini API Key (optional for mock mode, required for live AI extraction)
GEMINI_API_KEY=

# Gemini Model Selection (default: gemini-1.5-flash; also supports gemini-2.0-flash)
GEMINI_MODEL=gemini-1.5-flash

# TinyFish API Key (optional for mock mode, required for live web crawling)
TINYFISH_API_KEY=

# Async SQLite Database Connection URL
DATABASE_URL=sqlite+aiosqlite:///backend/data/leadforge.db

# Allowed CORS Origins (supports comma-separated string or JSON list)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## Quality & Test Verification

Run all test suites and quality gates:

```powershell
# Run full backend pytest suite (102 tests)
..\.venv\Scripts\python.exe -m pytest backend/app/tests -v

# Run Ruff linter
..\.venv\Scripts\python.exe -m ruff check backend

# Run Ruff format check
..\.venv\Scripts\python.exe -m ruff format backend --check

# Run Frontend production build
cd frontend; npm.cmd run build
```

---

## Security & Anti-Hallucination Controls

- **Verbatim Substring Verifier:** Any claim extracted by Gemini as `FACT` that fails an exact verbatim substring match against crawled text is automatically downgraded to `INFERENCE`.
- **CWE-1236 Defense:** CSV exports prefix potential formula trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`) with single quotes to prevent spreadsheet formula injection.
- **Zero Send:** The platform has no outbound email dispatch mechanisms. All outreach drafts are strictly presented for SDR review and 1-click clipboard copy.
- **Secret Isolation:** API keys are never exposed in logs, error payloads, or frontend bundles.

---

## License

MIT License. Developed by TriCode.
