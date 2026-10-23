# AI Agent Architecture & Epistemic Operating Guidelines
## Project: LeadForge — Evidence-First Sales Intelligence
**Document Version:** 1.0.0  
**AI Engines:** Google Gemini API (`gemini-1.5-flash` / `gemini-2.0-flash`)  
**Core Mandate:** Zero Hallucination, Explainable Epistemology, Strict Grounding

---

## 1. Role of AI in LeadForge

In LeadForge, Artificial Intelligence operates strictly as an **analytical synthesis and drafting assistant**, never as an autonomous decision-maker or email sender. The AI pipeline is bounded by strict structured outputs (JSON schemas), deterministic Python verification layers, and human-in-the-loop review.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Multi-Stage Agent Pipeline                             │
├────────────────────┬────────────────────┬───────────────────────┬──────────────────────┤
│ Stage 1            │ Stage 2            │ Stage 3               │ Stage 4              │
│ Web Scraper Worker │ Evidence Extractor │ Rubric Scoring Engine │ Outreach Generator   │
├────────────────────┼────────────────────┼───────────────────────┼──────────────────────┤
│ TinyFish API       │ Gemini API         │ Python 3.12 Engine    │ Gemini API           │
│ Captures raw HTML, │ Extracts quotes,   │ Computes 0–100 score  │ Writes cold email    │
│ text, & metadata   │ categorizes:       │ using deterministic   │ citing verified      │
│ across pages       │ FACT / INFERENCE / │ mathematical rubric   │ evidence items only  │
│                    │ UNKNOWN            │                       │                      │
└────────────────────┴────────────────────┴───────────────────────┴──────────────────────┘
```

---

## 2. Epistemic Status Framework

Every claim extracted by the system must be tagged with one of three mutually exclusive epistemic states:

```
                  ┌──────────────────────────────────────────────┐
                  │              EPISTEMIC STATES                │
                  └──────────────────────┬───────────────────────┘
                                         │
         ┌───────────────────────────────┼──────────────────────────────┐
         ▼                               ▼                              ▼
    ┌─────────┐                   ┌─────────────┐                ┌─────────────┐
    │  FACT   │                   │  INFERENCE  │                │   UNKNOWN   │
    └────┬────┘                   └──────┬──────┘                └──────┬──────┘
         │                               │                              │
Direct verbatim quote           Logical deduction from          Data absent from
backed by exact URL &           observed facts; reasoning       crawled public sources;
optional timestamp              must be explicitly stated       never guess or fabricate
```

### 2.1 The FACT Standard
* **Criterion:** The claim must be directly supported by a verbatim text excerpt (`exact_quote`) present in the scraped text of the target domain.
* **Requirements:**
  * Must specify the exact `source_url`.
  * Must include the exact verbatim quote without paraphrasing.
  * If a publication date exists in the source meta tags, it must be captured; otherwise, recorded as `null`.
* **Example:**
  * *Claim:* "Offers a starter plan priced at ₹499 per month for small retailers."
  * *Quote:* `"Starter plan: ₹499/month billed annually. Ideal for single-store retailers."`
  * *Source URL:* `https://khatabook.com/pricing`

### 2.2 The INFERENCE Standard
* **Criterion:** A logical, probabilistic conclusion derived from one or more facts, where the exact assertion was not explicitly written out.
* **Requirements:**
  * Must clearly articulate `gemini_reasoning` detailing how the conclusion was reached.
  * Must cite the underlying facts that support the inference.
  * Must never invent underlying premises.
* **Example:**
  * *Claim:* "Likely targets non-technical small merchants who prefer mobile-first workflows."
  * *Reasoning:* "The product emphasizes an Android APK download on the homepage, highlights WhatsApp notification sync, and provides a 1-click OTP signup without email requirements."

### 2.3 The UNKNOWN Standard
* **Criterion:** A critical evaluation criterion (e.g., funding amount, exact user count, API availability) for which no credible information was found on the crawled pages.
* **Requirements:**
  * Must explicitly record the absence of data.
  * **Absolute Prohibition:** The model must **never** extrapolate, speculate, or invent numbers, names, or buying triggers when data is missing.
* **Example:**
  * *Claim:* "Total active merchant volume or annual GMV is not publicly disclosed on the website."
  * *Quote:* `null`
  * *Source URL:* `null`

---

## 3. Explainable 100-Point Lead Scoring Rubric

Lead scores are calculated using a transparent, deterministic mathematical rubric implemented in Python. The LLM provides the verified traits; the Python engine calculates the score.

```
Total Lead Score (0–100) = SMB Focus (35) + SaaS Model (25) + Growth Signals (20) + Evidence Quality (20)
```

| Rubric Dimension | Max Points | Evaluation Criteria | Scoring Rules |
|---|---|---|---|
| **1. SMB Focus in India** | **35 pts** | • Primary audience is Indian MSMEs, Kiranas, or small businesses<br>• Local currency pricing (INR / ₹)<br>• Mobile-first / vernacular / WhatsApp capabilities | • Explicit MSME / SME focus: **+15 pts**<br>• Indian Rupee (INR / ₹) pricing: **+10 pts**<br>• Low-friction / mobile / WhatsApp onboarding: **+10 pts** |
| **2. SaaS Delivery Model** | **25 pts** | • Cloud-hosted software delivery<br>• Recurring subscription or transaction-based billing<br>• Self-serve signup or transparent tier structure | • Cloud / SaaS architecture verified: **+15 pts**<br>• Transparent self-serve or tier pricing: **+10 pts** |
| **3. Growth & Market Signals** | **20 pts** | • Recent product launch, update, or blog within 12 months<br>• Active hiring or leadership expansion announcements | • Fresh update / blog verified (< 12 mo): **+10 pts**<br>• Hiring / scaling / partner signals present: **+10 pts** |
| **4. Evidence Quality** | **20 pts** | • High ratio of verified `FACT` items vs `UNKNOWN` items<br>• Multi-page crawl verification (pricing + product + about) | • 3+ verified facts with verbatim quotes: **+10 pts**<br>• Multiple distinct URLs successfully cited: **+10 pts** |

---

## 4. Agent Prompts & Structured Schemas

### 4.1 Evidence Extraction Agent Prompt

```text
You are the Evidence Extraction Specialist for LeadForge, an evidence-first sales intelligence platform.
Your objective is to extract structured company facts, reasoned inferences, and critical unknowns from the provided website content of an Indian SaaS company.

TARGET ICP PROFILE:
- Vertical: B2B SaaS serving SMBs / MSMEs in India
- Geography: India
- Key Features: Low barrier to entry, INR pricing, mobile / WhatsApp readiness

STRICT OPERATING RULES:
1. Grounding: Every claim marked as FACT must contain an EXACT, VERBATIM quote from the provided text. Do not paraphrase facts.
2. Inference Transparency: Any deductive reasoning must be marked as INFERENCE and include your step-by-step reasoning in 'gemini_reasoning'.
3. Acknowledged Gaps: If an ICP requirement cannot be confirmed from the text, create an item with status UNKNOWN. Do not guess.
4. Publication Dates: Extract published dates from blog posts or press snippets if present; otherwise return null.
5. You must output valid JSON matching the specified schema.

INPUT SCRAPED TEXT:
{scraped_content_xml}
```

#### JSON Response Schema (`EvidenceExtractionResponse`):
```json
{
  "type": "object",
  "properties": {
    "company_name": { "type": "string" },
    "hq_location": { "type": "string", "nullable": true },
    "employee_range": { "type": "string", "nullable": true },
    "evidence_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "category": { 
            "type": "string", 
            "enum": ["SMB_FOCUS", "SAAS_MODEL", "GROWTH_SIGNAL", "TECH_FIT", "COMPANY_PROFILE"] 
          },
          "rubric_criterion": { 
            "type": "string", 
            "nullable": true,
            "enum": [
              "MSME_EXPLICIT_FOCUS",
              "INR_PRICING",
              "MOBILE_WHATSAPP_ONBOARDING",
              "CLOUD_SAAS_ARCHITECTURE",
              "TRANSPARENT_TIER_PRICING",
              "RECENT_PRODUCT_UPDATE",
              "HIRING_EXPANSION_SIGNAL",
              "NONE"
            ]
          },
          "claim_text": { "type": "string" },
          "exact_quote": { "type": "string", "nullable": true },
          "epistemic_status": { "type": "string", "enum": ["FACT", "INFERENCE", "UNKNOWN"] },
          "confidence_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "source_url": { "type": "string", "nullable": true },
          "publication_date": { "type": "string", "nullable": true },
          "gemini_reasoning": { "type": "string", "nullable": true }
        },
        "required": ["category", "claim_text", "epistemic_status", "confidence_score"]
      }
    }
  },
  "required": ["company_name", "evidence_items"]
}
```

> [!NOTE]
> **Model Configurability & Fallback:** The active Gemini model is driven by the `GEMINI_MODEL` environment variable (default: `gemini-1.5-flash`). If the requested model is unavailable, rate-limited, or when running offline, the system falls back seamlessly to deterministic mock evidence without crashing.

---

### 4.2 Grounded Outreach Draft Agent Prompt

```text
You are the Outreach Copywriting Specialist for LeadForge.
Your task is to draft a concise, consultative cold email (under 120 words) for a sales prospect.

STRICT GROUNDING RULES:
1. You may ONLY reference company attributes, milestones, or pricing details that are present in the provided APPROVED EVIDENCE LIST.
2. For every personalized sentence or claim in the email body, you MUST append a citation marker referencing the evidence item ID (e.g. "[Ref: #3]").
3. DO NOT fabricate mutual connections, past conversations, or unverified market gossip.
4. Tone: Professional, consultative, direct, respectful of founder/SDR time.
5. NO OUTBOUND SENDING: You are generating a review draft only.

APPROVED EVIDENCE LIST:
{approved_evidence_json}
```

#### JSON Response Schema (`OutreachDraftResponse`):
```json
{
  "type": "object",
  "properties": {
    "subject_line": { "type": "string" },
    "body_text": { "type": "string" },
    "referenced_evidence_ids": {
      "type": "array",
      "items": { "type": "integer" }
    },
    "word_count": { "type": "integer" }
  },
  "required": ["subject_line", "body_text", "referenced_evidence_ids", "word_count"]
}
```

---

## 5. Anti-Hallucination & Verification Safeguards

To maintain zero tolerance for false information, the backend executes automated validation:

1. **SubString Verifier:** Before saving any `FACT` item to SQLite, the backend executes:
   ```python
   def verify_grounding(quote: str, raw_scraped_text: str) -> bool:
       if not quote:
           return False
       normalized_quote = " ".join(quote.lower().split())
       normalized_source = " ".join(raw_scraped_text.lower().split())
       return normalized_quote in normalized_source
   ```
2. **Fallback Action:** If `verify_grounding` returns `False`, the item's epistemic status is automatically degraded to `INFERENCE` or rejected, and an alert is logged to `audit_logs`.
3. **Human-in-the-Loop Review:** The user interface displays inline badge indicators and enables manual editing before any draft can be copied or exported.
