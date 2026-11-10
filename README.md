# LeadForge — Evidence-First Sales Intelligence for B2B SaaS

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-129%20Passing-brightgreen.svg)]()
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
5. **Custom Prospect Ingestion & Deduplication:** In addition to the 10 pre-loaded Indian SaaS demo companies, users can add any company with its name and website URL (`POST /api/prospects`). The system validates the HTTP/HTTPS address, derives and normalizes the root domain, guards against duplicates (HTTP 409), and enables on-demand TinyFish crawling and Gemini evidence extraction.
6. **General-Purpose Web Search (Tavily):** Unrestricted internet search for any topic, technology trend, or organization using exact natural-language queries without keyword alteration or industry restriction. Search results display rich source metadata and offer one-click candidate ingestion into LeadForge with duplicate-domain defense.

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

- **Backend:** Python 3.12, FastAPI, SQLAlchemy (asyncio), Dual Database Support: SQLite WAL mode (`aiosqlite`) locally & Neon Serverless PostgreSQL (`asyncpg`) in production, Pydantic v2 Settings.
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React.
- **AI & Crawling:** Google Gemini API (`gemini-2.5-flash` / `gemini-3.8-flash`), TinyFish Public Web Scraping API.
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

## Zero-Cost Deployment Architecture (₹0 / month)

LeadForge is engineered to run at **₹0 recurring monthly cost** within genuine, documented free-tier quotas:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LEADFORGE ₹0/MONTH ZERO-COST ARCHITECTURE                       │
├──────────────────────────┬─────────────────────────────┬───────────────────────────────┤
│ Frontend (Client)        │ Backend (API & Pipeline)    │ Database (Persistence)        │
├──────────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ Cloudflare Pages         │ Render Free Web Service     │ Neon Serverless PostgreSQL    │
│ • Vite React 18 SPA      │ • Python 3.12 FastAPI       │ • SQLAlchemy (asyncpg)        │
│ • Unlimited bandwidth    │ • 750 free instance hrs/mo  │ • 1 GB persistent storage     │
│ • Global Anycast CDN     │ • Scales to zero after 15m  │ • Never deleted or paused     │
│ • No credit card needed  │ • No credit card needed     │ • No credit card needed       │
│ • Monthly Cost: ₹0       │ • Monthly Cost: ₹0          │ • Monthly Cost: ₹0            │
└──────────────────────────┴─────────────────────────────┴───────────────────────────────┘
```

### 1. Frontend: Cloudflare Pages (₹0/mo)
- **Deployment:** Connect GitHub repo to Cloudflare Pages.
- **Build settings:**
  - Framework: Vite
  - Build command: `npm run build`
  - Output directory: `dist`
  - Root directory: `frontend`
- **Environment variables:** Set `VITE_API_URL` to your backend public URL (e.g. `https://leadforge-backend.onrender.com/api`).
- **Quotas:** Unlimited bandwidth, 500 builds/month, 100% free with no credit card required.

### 2. Backend: Render Free Web Service (₹0/mo)
- **Deployment:** Deploy via `render.yaml` (`plan: free`) or connect GitHub repo to Render as a Web Service.
- **Runtime:** Docker (`backend/Dockerfile`).
- **Health Check:** `/api/health`.
- **Stateless Operation:** Connects to an external persistent database (Neon Serverless Postgres), eliminating ephemeral storage data loss when the free container sleeps after 15 minutes of inactivity.

### 3. Database: Neon Serverless PostgreSQL (₹0/mo)
- **Persistence:** 1 GB free persistent storage. Unlike Render's free 30-day trial databases, Neon databases **never expire or auto-delete**.
- **Connection:** Provide `DATABASE_URL=postgresql+asyncpg://<user>:<password>@<neon-host>/<dbname>` in Render backend environment variables.
- **Local SQLite Preservation:** Local development and testing continue using local SQLite (`leadforge.db`) with zero external dependencies.

---

## Alternative Deployment Options

### Option A: Local / Virtual Server with Docker Compose
Run the complete multi-container production stack locally or on an existing server:

```powershell
docker-compose up --build -d
```
- Frontend: `http://localhost:80`
- Backend: `http://localhost:8000/api`
- Persistence: Stored in named volume `leadforge_sqlite_data` mounted at `/app/backend/data`.

### Option B: Render Starter Plan (Optional Paid Convenience)
If you prefer an all-in-one single-provider container deployment with persistent disk instead of external Postgres:
- Requires Render **Starter plan** ($7/mo instance + $0.25/GB/mo for 1GB disk).
- Mounts `/app/backend/data` directly to a Render persistent block disk.

---

## Operational & Verification States

LeadForge clearly distinguishes between 5 operational and deployment states:

| State | Scope | Description & Indicators |
|---|---|---|
| **1. Local Mock Mode** | Local / Offline | Default mode (`USE_MOCK_APIS=true`). Serves deterministic fixtures for 10 Indian SaaS prospects. `/api/health` reports `MOCK`. |
| **2. Live API Configured** | Staging / Prod | `GEMINI_API_KEY` and `TINYFISH_API_KEY` set in environment (`USE_MOCK_APIS=false`). Health reports `LIVE_CONFIGURED` prior to handshake. |
| **3. Live API Verified** | Real Providers | Successful runtime HTTP 200 ping to Gemini model metadata endpoint. Health reports `LIVE_VERIFIED`. |
| **4. Deployment Configuration** | Infrastructure | Infrastructure manifests validated (`render.yaml`, `docker-compose.yml`) for zero-cost or volume persistence. |
| **5. Public Deployment** | Live Cloud | Deployed publicly on Cloudflare Pages + Render Free Web Service + Neon Postgres. |

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

# Gemini Model Selection (default: gemini-2.5-flash; also supports gemini-3.8-flash)
GEMINI_MODEL=gemini-2.5-flash

# TinyFish API Key (optional for mock mode, required for live web crawling)
TINYFISH_API_KEY=

# Database Connection URL (Async SQLite locally, or Neon Serverless PostgreSQL in production)
# Local:
DATABASE_URL=sqlite+aiosqlite:///backend/data/leadforge.db
# Production (Neon PostgreSQL with connection pooling):
# DATABASE_URL=postgresql+asyncpg://user:pass@ep-xyz-pooler.region.aws.neon.tech/leadforge?sslmode=require

# Allowed CORS Origins (supports comma-separated string or JSON list)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## Quality & Test Verification

Run all test suites and quality gates:

```powershell
# Run full backend pytest suite (110 tests)
.\.venv\Scripts\python.exe -m pytest backend/app/tests -v

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
