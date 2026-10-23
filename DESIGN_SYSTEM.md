# Design System & UI Specifications
## Project: LeadForge — Evidence-First Sales Intelligence
**Document Version:** 1.0.0  
**Framework:** React 18+  
**Styling Framework:** Tailwind CSS v3.4+  
**Design Philosophy:** "Evidence-First Clarity" — High Information Density, Transparent Epistemology, Zero Clutter

---

## 1. Aesthetic Philosophy & Visual Identity

LeadForge is a specialized professional tool for sales researchers, growth engineers, and founders. Its visual language prioritizes:
1. **Immediate Epistemic Legibility:** The user must be able to glance at any screen and instantly distinguish confirmed facts from AI inferences and acknowledged unknowns.
2. **High Information Density:** Avoid excessive whitespace or oversized marketing cards; prioritize compact tables, clean metadata badges, and readable monospace quotes.
3. **Auditability:** Every metric or claim offers an interactive path to inspect its source URL, verbatim text snippet, and publication timestamp.
4. **Professional Dark/Light Balance:** Built on a deep slate/indigo theme that conveys analytical rigor and precision.

---

## 2. Color Palette & Token Definitions

Tailwind CSS color scales are mapped semantically to establish consistency across the interface.

```
┌─────────────────────────────────────────────────────────────┐
│                      Semantic Color Tokens                   │
├──────────────────┬─────────────────┬────────────────────────┤
│ Token            │ Tailwind Class  │ Primary Purpose        │
├──────────────────┼─────────────────┼────────────────────────┤
│ Canvas / BG      │ slate-50 / 900  │ Background foundation  │
│ Surface / Card   │ white / 800     │ Container cards & rows │
│ Border / Divider │ slate-200 / 700 │ Subtle separation      │
│ Text Primary     │ slate-900 / 100 │ Headings & claim text  │
│ Text Muted       │ slate-500 / 400 │ Metadata & timestamps  │
│ Brand Primary    │ indigo-600      │ Primary action buttons │
│ FACT State       │ emerald-600     │ Confirmed web evidence │
│ INFERENCE State  │ amber-600       │ Logical deduction tag  │
│ UNKNOWN State    │ slate-500       │ Acknowledged gap       │
│ Score High (80+) │ emerald-600     │ High ICP alignment     │
│ Score Med (50-79)│ amber-600       │ Moderate fit           │
│ Score Low (<50)  │ slate-400       │ Disqualified or weak   │
└──────────────────┴─────────────────┴────────────────────────┘
```

### 2.1 Epistemic Status Color Mapping
* **FACT (Verified):**
  * Badge Background: `bg-emerald-50 dark:bg-emerald-950/40`
  * Badge Text: `text-emerald-700 dark:text-emerald-300`
  * Badge Border: `border-emerald-200 dark:border-emerald-800`
  * Icon: Checkmark Circle (`✓ FACT`)
* **INFERENCE (Deduction):**
  * Badge Background: `bg-amber-50 dark:bg-amber-950/40`
  * Badge Text: `text-amber-700 dark:text-amber-300`
  * Badge Border: `border-amber-200 dark:border-amber-800`
  * Icon: Sparkles / Lightbulb (`⚡ INFERENCE`)
* **UNKNOWN (Data Absent):**
  * Badge Background: `bg-slate-100 dark:bg-slate-800`
  * Badge Text: `text-slate-600 dark:text-slate-400`
  * Badge Border: `border-slate-200 dark:border-slate-700`
  * Icon: Question Circle (`? UNKNOWN`)

---

## 3. Typography Scale & Guidelines

* **Primary Font Family:** `Inter`, system-ui, -apple-system, sans-serif.
* **Code / Citation Font Family:** `JetBrains Mono`, `Fira Code`, monospace (for exact quote excerpts and URLs).

| Style | Tailwind Classes | Usage |
|---|---|---|
| **H1 Screen Title** | `text-2xl font-bold tracking-tight text-slate-900` | Top header, main page view |
| **H2 Section Title** | `text-lg font-semibold text-slate-800` | Table headers, modal titles |
| **H3 Card Title** | `text-base font-medium text-slate-900` | Prospect company names |
| **Body Standard** | `text-sm font-normal text-slate-700 leading-relaxed` | Descriptions, draft body text |
| **Body Metadata** | `text-xs font-normal text-slate-500` | Source URLs, publication dates, status |
| **Verbatim Quote** | `text-xs font-mono bg-slate-50 text-slate-800 p-2 border-l-2` | Scraped text citations |

---

## 4. Core UI Components

### 4.1 Prospect List Table
* Fixed header with sortable columns: `Company`, `Domain`, `Status`, `Lead Score`, `Verified Facts`, `Inferences`, `Actions`.
* Hover state: subtle background transition (`hover:bg-slate-50/80 transition-colors`).
* Action buttons:
  * "Research" (Triggers TinyFish + Gemini pipeline)
  * "Inspect Evidence" (Opens side drawer with citations)
  * "Outreach Draft" (Opens modal with grounded copy)

### 4.2 Lead Score Indicator Pill
* Visual presentation: Compact badge containing a numerical score (0–100) alongside a miniature circular progress ring or colored pill.
* Interactive tooltip: Hovering reveals the 4-category score breakdown (SMB Focus, SaaS Model, Growth Signals, Evidence Quality).

### 4.3 Evidence Inspector Drawer
A right-hand slide-out drawer displaying all atomic evidence items associated with a prospect:
1. Category chip (`SMB_FOCUS`, `PRICING`, `PRODUCT`, etc.).
2. Epistemic Badge (`FACT` vs. `INFERENCE` vs. `UNKNOWN`).
3. Summary claim text.
4. Blockquote containing the verbatim `exact_quote`.
5. Clickable source link with domain favicon and extracted publication date (e.g., `Published: 14 Oct 2024` or `Date: Not found`).
6. AI reasoning note (present whenever the item is an `INFERENCE`).

### 4.4 Grounded Outreach Modal
* Top banner: **Zero Auto-Send Notice** (`🔒 Outbound transmission disabled. Human review required.`).
* Editable email subject line and body area.
* Side-by-side or bottom citation reference panel displaying each fact referenced in the email.
* "Copy to Clipboard" button with transient confirmation toast.

---

## 5. Design Tokens (Tailwind Configuration Extension)

```javascript
// tailwind.config.js
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          900: '#312e81',
        },
        epistemic: {
          fact: '#059669',      // emerald-600
          inference: '#d97706', // amber-600
          unknown: '#64748b',   // slate-500
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
};
```

---

## 6. Accessibility & Usability Standards

* **Contrast Ratios:** All text and badge color pairings meet WCAG 2.1 AA requirements (minimum 4.5:1 contrast for normal text).
* **Keyboard Navigation:** Modals, drawers, and table actions are fully navigable via `Tab`, `Esc`, and `Enter`.
* **Distinct States:** Epistemic badges never rely solely on color; every badge includes explicit text labels (`FACT`, `INFERENCE`, `UNKNOWN`) and distinct icons.
