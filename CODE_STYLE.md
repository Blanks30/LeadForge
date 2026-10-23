# Code Style & Engineering Standards
## Project: LeadForge — Evidence-First Sales Intelligence
**Document Version:** 1.0.0  
**Languages:** Python 3.12 (Backend) | JavaScript / JSX (Frontend)  
**Tooling:** Ruff (Python) | Prettier + ESLint (Frontend) | Git

---

## 1. Guiding Principles

1. **Explicit Over Implicit:** Never hide business logic in magical metaprogramming or complex inheritance hierarchies. Keep data pipelines transparent and linear.
2. **Defensive Against Incomplete Data:** Scraped web data is inherently noisy. Always handle missing fields, null publication dates, and ambiguous text gracefully.
3. **Fail Fast with Clear Diagnostics:** Validate schemas at the boundaries (API entry, LLM response, database input).
4. **Zero Untyped Backend Code:** All Python functions, methods, and schemas must feature complete Python 3.12 type annotations.

---

## 2. Python 3.12 Backend Conventions

### 2.1 Language Features & Type Annotations
* Use modern Python 3.12 native union syntax: `str | None` instead of `Optional[str]`.
* Use native generic collections: `list[str]`, `dict[str, Any]` instead of importing from `typing`.
* Always annotate function signatures and return types:
  ```python
  # Good
  async def calculate_lead_score(
      prospect_id: int,
      evidence_items: list[EvidenceItem]
  ) -> tuple[int, dict[str, int]]:
      ...

  # Bad
  def calculate_lead_score(prospect_id, items):
      ...
  ```

### 2.2 Pydantic v2 Guidelines
* All data transfer objects (DTOs) and API contracts must be defined as Pydantic models.
* Use `model_config = ConfigDict(from_attributes=True)` for SQLAlchemy ORM compatibility.
* Use descriptive field constraints (`ge=0`, `le=100`, `min_length=1`).
  ```python
  from pydantic import BaseModel, Field, HttpUrl

  class ProspectSummary(BaseModel):
      id: int
      company_name: str = Field(min_length=1)
      domain: str = Field(pattern=r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
      lead_score: int = Field(ge=0, le=100)
      status: str
  ```

### 2.3 Formatting & Linting (Ruff)
The project utilizes **Ruff** for sub-second linting and formatting.

* **Line Length:** 88 characters.
* **Target Python Version:** `py312`.
* **Enabled Rule Sets:**
  * `E` / `W`: Pycodestyle errors and warnings.
  * `F`: Pyflakes.
  * `I`: isort (automatic import sorting).
  * `UP`: pyupgrade (enforces modern Python 3.12 syntax).
  * `B`: flake8-bugbear (common bug prevention).
  * `SIM`: flake8-simplify.

```toml
# backend/pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"] # Formatting handles line length

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 2.4 Error Handling & HTTP Exceptions
* Catch specific exceptions (e.g., `httpx.TimeoutException`, `pydantic.ValidationError`).
* Raise FastAPI `HTTPException` with structured JSON details:
  ```python
  # Good
  raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail={"error": "PROSPECT_NOT_FOUND", "message": f"Prospect {prospect_id} does not exist."}
  )
  ```

---

## 3. Frontend (React + Vite + Tailwind) Conventions

### 3.1 File Structure & Naming
* **React Components:** PascalCase with `.jsx` extension (e.g., `ProspectCard.jsx`, `EpistemicBadge.jsx`).
* **Custom Hooks:** camelCase prefixed with `use` (e.g., `useProspects.js`).
* **Utility Modules:** camelCase with `.js` extension (e.g., `formatters.js`, `apiClient.js`).
* **Constants:** UPPER_SNAKE_CASE in dedicated constants files (e.g., `EPISTEMIC_STATUSES`).

### 3.2 Component Architecture
* **Single Responsibility:** Keep components small (< 150 lines). If a component exceeds 150 lines, split sub-views or table cells into modular child components.
* **Pure Presentational Components:** Separate UI rendering from data fetching. Use custom hooks for data orchestration.
  ```jsx
  // Good: Focused, prop-driven component
  export function EpistemicBadge({ status }) {
    const config = {
      FACT: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', label: 'FACT' },
      INFERENCE: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', label: 'INFERENCE' },
      UNKNOWN: { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200', label: 'UNKNOWN' },
    }[status] || { bg: 'bg-slate-100', text: 'text-slate-500', border: 'border-slate-200', label: status };

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${config.bg} ${config.text} ${config.border}`}>
        {config.label}
      </span>
    );
  }
  ```

### 3.3 Tailwind CSS Class Ordering
Order utility classes logically from layout to surface properties:
1. **Layout / Display:** `flex`, `grid`, `block`, `relative`, `absolute`
2. **Box Model / Sizing:** `w-full`, `max-w-md`, `h-10`, `overflow-hidden`
3. **Spacing:** `p-4`, `px-3`, `py-2`, `m-2`, `gap-2`
4. **Typography:** `text-sm`, `font-semibold`, `text-slate-800`, `leading-relaxed`
5. **Surfaces & Borders:** `bg-white`, `border`, `border-slate-200`, `rounded-lg`, `shadow-sm`
6. **Interactivity & Transitions:** `hover:bg-slate-50`, `focus:outline-none`, `transition-colors`

---

## 4. Git & Version Control Standards

### 4.1 Conventional Commits
All commit messages must adhere to the Conventional Commits specification:

* `feat: add 100-point rubric scoring engine`
* `fix: correct publication date parser for missing meta tags`
* `docs: update DATABASE.md with foreign key cascade policy`
* `test: add unit tests for epistemic classification schemas`
* `refactor: extract TinyFish crawler logic into dedicated service`
* `chore: configure ruff and pre-commit hooks`

### 4.2 Branching & Workflow
* `main`: Always deployable and passing all tests.
* Feature branches: `feat/rubric-engine`, `fix/tinyfish-timeout`, `docs/api-spec`.
* No sensitive tokens (`.env`, SQLite databases, API keys) may ever be committed.

---

## 5. Pre-Merge Verification Checklist

Before opening a pull request or completing a phase:
- [ ] `ruff check backend/` passes with 0 warnings or errors.
- [ ] `ruff format backend/ --check` confirms proper code formatting.
- [ ] `pytest backend/` executes with 100% passing tests.
- [ ] No `console.log` statements left in production frontend files.
- [ ] All new database queries use parameterized SQL / ORM filters.
