# Product Requirements Document (PRD)
## Project: LeadForge — Evidence-First Sales Intelligence
**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Target Completion:** 3–5 Focused Days (MVP)  
**Target Market:** Indian B2B SaaS Ecosystem (SMB Focused)

---

## 1. Executive Summary & Problem Statement

### 1.1 The Problem
Sales Development Representatives (SDRs) and founders targeting high-growth SaaS prospects spend hours manually sifting through company websites, press releases, and blogs to uncover personalization hooks. Current AI sales tools frequently fabricate information—inventing employee counts, misattributing target markets, or hallucinating buying signals. This damages credibility and violates trust.

### 1.2 The Solution
**LeadForge** is an evidence-first sales research tool. It accepts an Ideal Customer Profile (ICP), gathers real-time public data from target company websites using the **TinyFish API**, and analyzes the findings with the **Gemini API**. Crucially, LeadForge enforces strict epistemic categorization (distinguishing **Verified Facts**, **Inferences**, and **Unknowns**), scores leads against an explainable rubric, and crafts outreach emails grounded exclusively in verified citations. No emails are ever sent automatically.

---

## 2. Target Market & User Persona

### 2.1 Target Market
- **Geographic Focus:** India.
- **Industry Vertical:** B2B SaaS companies whose primary or significant customer segment is Small and Medium Businesses (SMBs) in India (e.g., billing/invoicing, SME ERP, merchant tech, logistics, vertical SaaS).
- **Target Batch Size:** 10 curated prospect companies for the initial MVP evaluation.

### 2.2 Primary Persona
* **Name:** Aarav Mehta
* **Role:** Lead SDR / Growth Founder at an API infrastructure startup.
* **Goal:** Reach out to 10 qualified Indian SaaS prospects with hyper-specific, zero-fluff cold emails.
* **Frustrations:** "Generic AI emails talk about vague synergies. I need to cite an exact sentence from their pricing page or product update, or I won't send it."
* **Key Requirement:** Must see the exact source URL, quote, and whether a claim is a proven fact or an inference before approving outreach.

---

## 3. Scope & MVP Phased Roadmap (3–5 Days)

To ensure completion within the 3–5 day window without technical debt, the project is scoped into 5 sequential phases:

| Phase | Duration | Scope | Deliverables |
|---|---|---|---|
| **Phase 1** | Day 1 | Setup & Data Architecture | FastAPI backend skeleton, SQLite database schema, Pydantic models, TinyFish client wrapper with mock fixtures. |
| **Phase 2** | Day 2 | Web Scraping & Evidence Extraction | TinyFish crawling pipeline, Gemini evidence extraction with Fact/Inference/Unknown categorization, source URL/quote storage. |
| **Phase 3** | Day 3 | Rubric Scoring & Outreach Engine | 100-point explainable lead scoring engine, grounded email draft generator, anti-hallucination validation. |
| **Phase 4** | Day 4 | User Interface & Export | React + Vite + Tailwind CSS dashboard, prospect detail modal, epistemic badge indicators, CSV export. |
| **Phase 5** | Day 5 | Testing, Hardening & Acceptance | Integration tests, edge-case validation (missing dates, blocked sites), security audit, documentation review. |

---

## 4. Core Workflow & Functional Requirements

The application follows an end-to-end 7-step workflow:

```
[1. ICP Definition] 
        │
        ▼
[2. TinyFish Web Research] 
        │
        ▼
[3. Evidence & Citation Capture] 
        │
        ▼
[4. Epistemic Categorization (Fact / Inference / Unknown)] 
        │
        ▼
[5. Explainable Lead Scoring (0–100 Rubric)] 
        │
        ▼
[6. Grounded Email Draft Generation] 
        │
        ▼
[7. Review, Local Save & CSV Export]
```

### 4.1 Step 1: Ideal Customer Profile (ICP) Input
* **FR-1.1:** The user can configure target ICP parameters:
  * Target Vertical (e.g., "B2B SaaS serving SMBs / Kirana / MSME in India").
  * Target Geography (default: "India").
  * Minimum / Preferred features (e.g., self-serve tier, Indian currency pricing, WhatsApp integration).
* **FR-1.2:** The system provides default pre-loaded presets tailored for Indian SMB SaaS.

### 4.2 Step 2: Web Research via TinyFish API
* **FR-2.1:** Accept a list of up to 10 prospect domains (e.g., Khatabook, myBillBook, Dukaan, Shiprocket, Vyapar, Classplus, etc.).
* **FR-2.2:** TinyFish API crawls targeted pages: Homepage, About Us, Pricing, Product/Features, and Blog/Press releases.
* **FR-2.3:** Backend caches raw crawling results in SQLite to prevent redundant API calls and control costs.

### 4.3 Step 3: Evidence & Source Capture
* **FR-3.1:** For every discovered data point, record:
  * `source_url`: Full validated URL where the evidence was extracted.
  * `exact_quote`: Direct text snippet from the crawled page.
  * `publication_date`: Extracted timestamp or metadata date; marked `null` if not found.
  * `fetched_at`: UTC timestamp of the crawl.

### 4.4 Step 4: Epistemic Categorization (Fact vs. Inference vs. Unknown)
* **FR-4.1:** All claims must be tagged with one of three strict states:
  * **FACT:** Directly stated on the website, verified by exact quote and URL (e.g., "Plans start at ₹499/month").
  * **INFERENCE:** Plausible deduction derived from a fact, clearly flagged as an inference with reasoning (e.g., "Presence of UPI and Razorpay suggests an India-first transaction model").
  * **UNKNOWN:** Crucial ICP criteria where no public data was found (e.g., "Total active merchant count is Unknown").
* **FR-4.2:** No hallucinated facts or ungrounded claims are permitted.

### 4.5 Step 5: Explainable Lead Scoring (Rubric-Based)
* **FR-5.1:** Calculate an overall score from 0 to 100 based on a deterministic, documented rubric:
  * **SMB Focus in India (35 pts):** Explicit mention of Indian MSME/SMBs, local pricing (INR), regional language support.
  * **SaaS Delivery Model (25 pts):** Cloud-hosted, subscription/usage pricing, self-serve or product-led onboarding.
  * **Growth & Market Signals (20 pts):** Recent product releases, hiring pages, expansion blogs.
  * **Evidence Quality & Completeness (20 pts):** Ratio of verified facts to unknowns; availability of verifiable citations.
* **FR-5.2:** Provide a transparent score breakdown modal explaining point deductions and contributions.

### 4.6 Step 6: Grounded Outreach Draft Generation
* **FR-6.1:** Generate personalized cold email drafts using the Gemini API.
* **FR-6.2:** Strict Grounding Rule: Every personalized claim in the draft must map to an existing `evidence_item` citation.
* **FR-6.3:** Emails are presented in an editable preview with inline citation chips.
* **FR-6.4:** **Zero Auto-Send Guarantee:** The system contains zero email-sending mechanisms (no SMTP, SES, or external email APIs). The user can only copy to clipboard or export.

### 4.7 Step 7: Prospect Management & CSV Export
* **FR-7.1:** Prospects, scores, evidence items, and generated drafts are stored persistently in SQLite.
* **FR-7.2:** Export feature produces a clean, standards-compliant CSV file containing:
  * Company Name, Website Domain, Overall Lead Score, SMB Alignment, Key Fact 1, Key Fact 2, Evidence Source URLs, Outreach Subject Line, Outreach Body.

---

## 5. Non-Functional Requirements

### 5.1 Performance & Latency
* Page load time for saved prospects under 300ms.
* TinyFish crawler timeout capped at 30 seconds per domain.
* Gemini analysis pipeline asynchronous and non-blocking with UI progress indicators.

### 5.2 Reliability & Fault Tolerance
* Robust error handling for unreachable URLs, 403/404 HTTP errors, and bot protection barriers.
* Offline/Mock mode support for development and demonstration without consuming external API credits.

### 5.3 Cost & Resource Optimization
* Minimize Gemini token usage by extracting clean text snippets prior to prompt injection.
* Cache all crawled text in the local database to allow prompt iteration without re-crawling.

---

## 6. Acceptance Criteria (MVP Gate)

1. **Prospect Ingestion:** Successfully processes 10 distinct Indian SMB SaaS domains.
2. **Evidence Integrity:** 100% of generated outreach claims possess a corresponding source URL and quote snippet.
3. **Epistemic Classification:** All company traits are distinctly labeled as `FACT`, `INFERENCE`, or `UNKNOWN`.
4. **Scoring Explainability:** The score for each prospect displays the exact mathematical breakdown matching the rubric.
5. **No Secret Leakage:** Zero API keys present in frontend bundles or Git logs.
6. **CSV Export:** Generated CSV imports cleanly into Google Sheets/Excel without encoding errors.
7. **No Auto-Sending:** Complete absence of outbound mail drivers or background mailers.
