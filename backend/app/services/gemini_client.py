"""Google Gemini API client for evidence extraction and structured sales intelligence.

Enforces strict grounding, explainable reasoning, and deterministic JSON schemas
following AGENTS.md. Communicates asynchronously via httpx to official Gemini REST endpoints.
"""

import json
import logging
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings

logger = logging.getLogger("leadforge.gemini")

# Official verified Gemini models supported for structured output
SUPPORTED_GEMINI_MODELS: set[str] = {
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
}

DEFAULT_FALLBACK_MODEL = "gemini-1.5-flash"
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiError(Exception):
    """Base exception for Gemini API interactions."""


class GeminiConfigError(GeminiError):
    """Raised when configuration is missing or invalid."""


class GeminiAuthError(GeminiError):
    """Raised on 401 or 403 authentication/authorization failure."""


class GeminiRateLimitError(GeminiError):
    """Raised on 429 quota exhaustion or rate limits."""


class GeminiUnavailableError(GeminiError):
    """Raised on 500/502/503/504 server unavailable errors."""


class GeminiModelNotFoundError(GeminiError):
    """Raised on 404 when requested model does not exist."""


class GeminiNetworkError(GeminiError):
    """Raised on timeout or network connection failure."""


class GeminiMalformedResponseError(GeminiError):
    """Raised when output is invalid JSON or violates the required schema."""


# ---------------------------------------------------------------------------
# Structured Schemas (matching AGENTS.md §4.1)
# ---------------------------------------------------------------------------


class GeminiEvidenceItem(BaseModel):
    """Individual epistemic claim extracted from source text."""

    category: str = Field(
        description="Category: SMB_FOCUS, SAAS_MODEL, GROWTH_SIGNAL, TECH_FIT, COMPANY_PROFILE"
    )
    rubric_criterion: str | None = Field(
        default=None,
        description="Matched rubric criterion enum or None",
    )
    claim_text: str = Field(description="Clear statement of observed trait or gap")
    exact_quote: str | None = Field(
        default=None,
        description="Verbatim text excerpt if FACT; null if INFERENCE or UNKNOWN",
    )
    epistemic_status: str = Field(
        description="Epistemic status: FACT, INFERENCE, or UNKNOWN"
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
    )
    source_url: str | None = Field(
        default=None,
        description="Source URL where quote was found",
    )
    publication_date: str | None = Field(
        default=None,
        description="ISO publication date if detected, else null",
    )
    gemini_reasoning: str | None = Field(
        default=None,
        description="Deductive reasoning if INFERENCE; gap explanation if UNKNOWN",
    )


class GeminiExtractionResponse(BaseModel):
    """Complete structured extraction payload from Gemini."""

    company_name: str
    hq_location: str | None = None
    employee_range: str | None = None
    evidence_items: list[GeminiEvidenceItem] = Field(default_factory=list)


EVIDENCE_EXTRACTION_SYSTEM_PROMPT = """You are the Evidence Extraction Specialist for LeadForge, an evidence-first sales intelligence platform.
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
"""


def resolve_model_name(model_name: str | None) -> str:
    """Validate and normalize the Gemini model ID, falling back safely if unknown."""
    if not model_name:
        return DEFAULT_FALLBACK_MODEL
    cleaned = model_name.removeprefix("models/").strip().lower()
    if cleaned in SUPPORTED_GEMINI_MODELS:
        return cleaned
    logger.warning(
        "Configured Gemini model '%s' is not in verified list %s; defaulting to '%s'",
        model_name,
        SUPPORTED_GEMINI_MODELS,
        DEFAULT_FALLBACK_MODEL,
    )
    return DEFAULT_FALLBACK_MODEL


class GeminiClient:
    """Asynchronous HTTP client for Google Gemini REST API.

    Executes structured evidence extraction with strict schema validation,
    sensible timeouts, and comprehensive error handling.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 30.0,
        endpoint_override: str | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = resolve_model_name(model or settings.GEMINI_MODEL)
        self.timeout_seconds = timeout_seconds
        self.endpoint_override = endpoint_override

    @property
    def endpoint_url(self) -> str:
        """Construct the REST URL for the configured model."""
        if self.endpoint_override:
            return self.endpoint_override
        return f"{GEMINI_API_BASE_URL}/{self.model}:generateContent"

    def _build_prompt_payload(
        self,
        company_name: str,
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Construct prompt and structured JSON generationConfig."""
        content_lines: list[str] = [
            f"TARGET COMPANY: {company_name}",
            "",
            "INPUT SCRAPED TEXT:",
        ]
        for idx, src in enumerate(sources, 1):
            url = src.get("url", f"https://source-{idx}")
            page_type = src.get("page_type", "HOMEPAGE")
            snippet = src.get("raw_text_snippet", "")
            content_lines.append(
                f'<source index="{idx}" url="{url}" page_type="{page_type}">\n{snippet}\n</source>'
            )

        user_content = "\n\n".join(content_lines)

        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                f"{EVIDENCE_EXTRACTION_SYSTEM_PROMPT}\n\n"
                                f"{user_content}\n\n"
                                "Respond with a single valid JSON object strictly adhering to the schema."
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
        }

    async def extract_evidence(
        self,
        company_name: str,
        sources: list[dict[str, Any]],
    ) -> GeminiExtractionResponse:
        """Call Gemini API to extract grounded facts, inferences, and unknowns from sources.

        Never logs or exposes the API key. Validates response schemas strictly.
        """
        if not self.api_key:
            raise GeminiConfigError("GEMINI_API_KEY is not configured or is empty.")

        if not sources:
            raise GeminiMalformedResponseError(
                "Cannot extract evidence from empty sources list."
            )

        payload = self._build_prompt_payload(company_name, sources)
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
            "User-Agent": "LeadForge/0.1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    self.endpoint_url,
                    json=payload,
                    headers=headers,
                )
        except httpx.TimeoutException as exc:
            raise GeminiNetworkError(
                f"Gemini API request timed out after {self.timeout_seconds}s."
            ) from exc
        except httpx.RequestError as exc:
            raise GeminiNetworkError(
                f"Gemini API network connection failure: {exc.__class__.__name__}"
            ) from exc

        # Process HTTP response status
        status = response.status_code
        if status == 200:
            return self._parse_successful_response(response.text)

        if status in (401, 403):
            raise GeminiAuthError(
                f"Gemini authentication failed (HTTP {status}). Verify GEMINI_API_KEY."
            )
        if status == 404:
            raise GeminiModelNotFoundError(
                f"Gemini model '{self.model}' not found (HTTP 404). Check GEMINI_MODEL."
            )
        if status == 429:
            raise GeminiRateLimitError(
                "Gemini API rate limit or quota exceeded (HTTP 429). Please retry later."
            )
        if status in (500, 502, 503, 504):
            raise GeminiUnavailableError(
                f"Gemini service is temporarily unavailable (HTTP {status})."
            )

        raise GeminiError(
            f"Unexpected Gemini API error (HTTP {status}): {response.text[:200]}"
        )

    def _parse_successful_response(self, raw_body: str) -> GeminiExtractionResponse:
        """Parse Gemini response container, extract JSON text part, and validate schema."""
        try:
            root_data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise GeminiMalformedResponseError(
                "Gemini returned non-JSON HTTP response body."
            ) from exc

        candidates = root_data.get("candidates", [])
        if not candidates:
            # Check for safety rating blocks or empty responses
            prompt_feedback = root_data.get("promptFeedback", {})
            block_reason = prompt_feedback.get("blockReason", "No candidates returned")
            raise GeminiMalformedResponseError(
                f"Gemini returned no candidates (Reason: {block_reason})."
            )

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        if not parts or "text" not in parts[0]:
            raise GeminiMalformedResponseError(
                "Gemini candidate content contains no text parts."
            )

        text_content = parts[0]["text"].strip()

        # Handle potential markdown code fencing if returned by model
        if text_content.startswith("```json"):
            text_content = text_content.removeprefix("```json").removesuffix("```").strip()
        elif text_content.startswith("```"):
            text_content = text_content.removeprefix("```").removesuffix("```").strip()

        try:
            parsed_json = json.loads(text_content)
        except json.JSONDecodeError as exc:
            raise GeminiMalformedResponseError(
                f"Failed to parse model output text as JSON: {text_content[:200]}"
            ) from exc

        try:
            return GeminiExtractionResponse.model_validate(parsed_json)
        except ValidationError as exc:
            raise GeminiMalformedResponseError(
                f"Gemini JSON output violated schema: {exc}"
            ) from exc


def get_gemini_client() -> GeminiClient:
    """Factory function returning configured Gemini client instance."""
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
    )
