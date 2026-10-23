# Testing Strategy & Quality Assurance Plan
## Project: LeadForge — Evidence-First Sales Intelligence
**Document Version:** 1.0.0  
**Test Runners:** Pytest (Backend) | Vitest (Frontend)  
**Target Coverage:** > 80% Core Logic Coverage (Scoring, Extraction, Verification)

---

## 1. Testing Strategy & Philosophy

LeadForge deals with probabilistic AI outputs, unstructured web crawls, and rigorous evidence extraction. Therefore, testing focuses heavily on:
1. **Deterministic Grounding Verification:** Ensuring the system rejects hallucinated quotes or unverified claims.
2. **Deterministic Mocking:** Providing offline fixtures for TinyFish and Gemini so the entire test suite executes in < 10 seconds without internet access or API fees.
3. **Boundary & Edge-Case Resilience:** Testing 404s, bot blocks, missing publication dates, and ambiguous company copy.

```
                  ┌──────────────────────┐
                  │   Manual E2E & UI    │  10% (User acceptance, workflow)
                  ├──────────────────────┤
                  │  Integration Tests   │  30% (FastAPI endpoints, SQLite WAL)
                  ├──────────────────────┤
                  │ Unit & Schema Tests  │  60% (Rubric scoring, mocks, parsers)
                  └──────────────────────┘
```

---

## 2. Test Environment & Tooling

### 2.1 Backend Tooling
* `pytest`: Test runner.
* `pytest-asyncio`: Native async test execution for FastAPI and `aiosqlite`.
* `httpx`: Async HTTP client for invoking FastAPI test routes via `AsyncClient`.
* `pytest-mock`: Mocking external API interfaces.
* In-Memory SQLite (`sqlite+aiosqlite:///:memory:`): Clean, isolated database for each test run.

### 2.2 Mocking Infrastructure (`USE_MOCK_APIS=true`)
To ensure rapid iteration and zero API costs:
* **TinyFish Mock Client:** Returns realistic HTML and text snippets for the 10 target Indian SaaS companies (e.g., Khatabook's pricing page, myBillBook's feature list).
* **Gemini Mock Client:** Returns deterministic JSON matching the `EvidenceResponse` and `OutreachResponse` Pydantic schemas.

---

## 3. Test Suites & Key Scenarios

### 3.1 Unit Tests (`backend/app/tests/test_scoring.py`)
Tests the mathematical validity and logic of the 100-point rubric engine:
* **Scenario TS-1: Maximum Alignment Score**
  * *Input:* Prospect with explicit INR pricing, mobile-first MSME ledger, recent 2024 blog release, and verified citations.
  * *Expected Output:* Score >= 85, score breakdown sums exactly to total score.
* **Scenario TS-2: Non-SaaS Enterprise Disqualification**
  * *Input:* Enterprise consultancy with manual quotation workflows and no self-serve signals.
  * *Expected Output:* Score <= 30; points deducted in SaaS model category.
* **Scenario TS-3: Strict Range Clamping**
  * *Input:* Any synthetic evidence combination.
  * *Expected Output:* Score must satisfy `0 <= lead_score <= 100`.
* **Scenario TS-4: Deterministic Criterion Mapping**
  * *Input:* Evidence items tagged with explicit `rubric_criterion` keys (e.g., `MSME_EXPLICIT_FOCUS`, `INR_PRICING`).
  * *Expected Output:* Calculated score is 100% deterministic and reproducible across multiple test executions.

### 3.2 Evidence Extraction & Grounding Tests (`backend/app/tests/test_evidence.py`)
* **Scenario TE-1: Grounding Quote Verification (Pass)**
  * *Input:* Gemini returns quote `"Plans start at ₹499/month"` which exists verbatim in scraped source text.
  * *Expected Output:* Quote validated, saved with `epistemic_status="FACT"`.
* **Scenario TE-2: Hallucination Interception (Fail & Reject)**
  * *Input:* Gemini outputs a quote `"We serve over 10 million Indian shops"` which does **not** appear anywhere in the source snippet.
  * *Expected Output:* Validation logic flags quote as ungrounded, rejects the quote or converts status to `UNKNOWN`.
* **Scenario TE-3: Missing Publication Date Handling**
  * *Input:* Scraped page has no HTML meta tags or date headers.
  * *Expected Output:* `publication_date` is stored as `null` without throwing a runtime error.
* **Scenario TE-4: Epistemic Categorization Integrity**
  * *Input:* Gemini output contains items with statuses `FACT`, `INFERENCE`, and `UNKNOWN`.
  * *Expected Output:* Inferences must have non-empty `gemini_reasoning`; Unknowns must have null `exact_quote`.

### 3.3 API Route Integration Tests (`backend/app/tests/test_api_routes.py`)
* **Scenario TR-1: Health Endpoint**
  * `GET /api/health` returns `200 OK` and confirms database connectivity.
* **Scenario TR-2: Seed Data Loading**
  * `POST /api/prospects/seed` loads 10 unique Indian SaaS domains without duplicates.
* **Scenario TR-3: Research Pipeline Execution**
  * `POST /api/prospects/1/research` updates prospect status from `PENDING` -> `ANALYZED`, populates evidence items, and logs research event.
* **Scenario TR-4: CSV Export Formatting & Injection Protection**
  * `GET /api/export/csv` returns `text/csv` with valid UTF-8 encoding, correct headers, and escaped quotation marks.

### 3.4 Security & Safety Audit Tests
* **Scenario TS-SEC1: Absence of Mail Dispatchers**
  * Automated static check ensuring that `smtplib`, `sendgrid`, `boto3.ses`, `mailgun`, and `resend` are completely absent from imports and project dependencies.
* **Scenario TS-SEC2: CSV Formula Injection Defense**
  * *Input:* Synthetic prospect claim beginning with `=cmd|' /C calc'!A0` or `+2+5`.
  * *Expected Output:* Output CSV serializes cell prefixed with `'` (e.g., `'=cmd...`), neutralizing formula execution.

---

## 4. Frontend Component Tests (`frontend/src/tests/`)

* **Badge Rendering (`EpistemicBadge.test.jsx`):**
  * Verifies correct CSS colors and icon labels for `FACT`, `INFERENCE`, and `UNKNOWN`.
* **Score Pill Tooltip (`ScoreBadge.test.jsx`):**
  * Verifies tooltip displays all 4 breakdown categories upon mouse hover.
* **Copy-to-Clipboard (`OutreachModal.test.jsx`):**
  * Verifies clicking "Copy Email" invokes `navigator.clipboard.writeText` and renders transient feedback.
* **Zero Send Assurance:**
  * Asserts that no "Send Email" button exists in the DOM.

---

## 5. Acceptance Test Checklist (MVP Sign-Off Gate)

Before the MVP is deemed ready for production review, all items must be checked:

| Category | Acceptance Criteria | Verification Method |
|---|---|---|
| **Prospect Discovery** | 10 Indian SaaS prospects seeded and viewable in dashboard | UI Inspection & `GET /api/prospects` |
| **Scraping** | TinyFish retrieves and caches HTML/markdown for target domains | Inspect `web_sources` table in SQLite |
| **Evidence Extraction** | Claims tagged as FACT, INFERENCE, or UNKNOWN with citations | Inspect `evidence_items` table in SQLite |
| **Scoring** | Explainable 0–100 score computed via documented rubric | Validate score calculation against rubric |
| **Grounded Outreach** | Email drafts cite specific evidence IDs with zero hallucinated quotes | Audit draft citations in UI modal |
| **Export** | CSV export downloads cleanly and opens in Excel/Google Sheets | Download CSV and verify columns |
| **Security** | Zero API keys in frontend code; zero mail-sending drivers | Source inspection & dependency audit |
| **Offline Capability** | Full test suite and UI can run using mock providers | Run with `USE_MOCK_APIS=true` |
