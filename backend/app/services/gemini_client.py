"""Google Gemini API client for evidence extraction and grounded outreach drafting.

Enforces strict grounding, explainable reasoning, and deterministic JSON schemas
following AGENTS.md §4.1 (evidence extraction) and §4.2 (outreach drafting).
Communicates asynchronously via httpx to official Gemini REST endpoints.
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
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
}

DEFAULT_FALLBACK_MODEL = "gemini-2.5-flash"
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
# Structured Schemas (matching AGENTS.md §4.1 and §4.2)
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
    """Complete structured extraction payload from Gemini (AGENTS.md §4.1)."""

    company_name: str
    hq_location: str | None = None
    employee_range: str | None = None
    evidence_items: list[GeminiEvidenceItem] = Field(default_factory=list)


class GeminiOutreachDraftResponse(BaseModel):
    """Structured outreach email draft validated against AGENTS.md §4.2 schema."""

    subject_line: str = Field(description="Compelling, personalized email subject line")
    body_text: str = Field(description="Consultative cold email body under 120 words")
    referenced_evidence_ids: list[int] = Field(
        default_factory=list,
        description="Evidence item IDs cited inline as [Ref: #N]",
    )
    word_count: int = Field(description="Accurate word count of body_text")


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

OUTREACH_DRAFT_SYSTEM_PROMPT = """You are the Outreach Copywriting Specialist for LeadForge.
Your task is to draft a concise, consultative cold email (under 120 words) for a sales prospect.

STRICT GROUNDING RULES:
1. You may ONLY reference company attributes, milestones, or pricing details that are present in the provided APPROVED EVIDENCE LIST.
2. For every personalized sentence or claim in the email body, you MUST append a citation marker referencing the evidence item ID (e.g. "[Ref: #3]").
3. DO NOT fabricate mutual connections, past conversations, or unverified market gossip.
4. Tone: Professional, consultative, direct, respectful of founder/SDR time.
5. NO OUTBOUND SENDING: You are generating a review draft only.
6. Keep word_count accurate — count every word in body_text.
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

    Executes structured evidence extraction and outreach drafting with strict schema
    validation, sensible timeouts, and comprehensive error handling.
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
        """Construct evidence-extraction prompt and structured JSON generationConfig."""
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

    def _build_outreach_prompt_payload(
        self,
        company_name: str,
        approved_evidence: list[dict[str, Any]],
        tone: str = "CONSULTATIVE_DIRECT",
    ) -> dict[str, Any]:
        """Construct the outreach draft prompt following AGENTS.md §4.2."""
        evidence_json = json.dumps(approved_evidence, indent=2)
        user_content = (
            f"TARGET COMPANY: {company_name}\n"
            f"TONE: {tone}\n\n"
            f"APPROVED EVIDENCE LIST:\n{evidence_json}\n\n"
            "Draft the cold email now. Respond with a single valid JSON object strictly adhering to the schema."
        )

        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": (f"{OUTREACH_DRAFT_SYSTEM_PROMPT}\n\n{user_content}")}
                    ],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.3,
            },
        }

    async def _post_to_gemini(self, payload: dict[str, Any]) -> str:
        """Execute the HTTP POST to Gemini and return the raw 200 response text.

        Raises typed GeminiError subclasses on all failure modes.
        Never logs or exposes the API key.
        """
        if not self.api_key:
            raise GeminiConfigError("GEMINI_API_KEY is not configured or is empty.")

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

        status = response.status_code
        if status == 200:
            return response.text
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
        raw_body = await self._post_to_gemini(payload)
        return self._parse_extraction_response(raw_body)

    async def generate_outreach_draft(
        self,
        company_name: str,
        approved_evidence: list[dict[str, Any]],
        tone: str = "CONSULTATIVE_DIRECT",
    ) -> GeminiOutreachDraftResponse:
        """Call Gemini to generate a grounded cold email draft citing only approved evidence.

        Follows AGENTS.md §4.2: subject line + body under 120 words + citation markers.
        Never logs or exposes the API key. Validates response schema strictly.
        """
        if not self.api_key:
            raise GeminiConfigError("GEMINI_API_KEY is not configured or is empty.")

        if not approved_evidence:
            raise GeminiMalformedResponseError(
                "Cannot generate outreach draft from empty evidence list."
            )

        payload = self._build_outreach_prompt_payload(
            company_name, approved_evidence, tone
        )
        raw_body = await self._post_to_gemini(payload)
        return self._parse_outreach_response(raw_body)

    def _parse_extraction_response(self, raw_body: str) -> GeminiExtractionResponse:
        """Parse and validate the Gemini evidence extraction response."""
        return self._parse_gemini_response(raw_body, GeminiExtractionResponse, "schema")

    def _parse_outreach_response(self, raw_body: str) -> GeminiOutreachDraftResponse:
        """Parse and validate the Gemini outreach draft response."""
        return self._parse_gemini_response(
            raw_body, GeminiOutreachDraftResponse, "outreach schema"
        )

    def _parse_gemini_response(
        self,
        raw_body: str,
        model_cls: type,
        schema_label: str,
    ) -> Any:
        """Shared Gemini response parsing: JSON decode, candidate extraction, schema validation."""
        try:
            root_data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise GeminiMalformedResponseError(
                "Gemini returned non-JSON HTTP response body."
            ) from exc

        candidates = root_data.get("candidates", [])
        if not candidates:
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

        # Strip optional markdown code fencing returned by some model variants
        if text_content.startswith("```json"):
            text_content = (
                text_content.removeprefix("```json").removesuffix("```").strip()
            )
        elif text_content.startswith("```"):
            text_content = text_content.removeprefix("```").removesuffix("```").strip()

        try:
            parsed_json = json.loads(text_content)
        except json.JSONDecodeError as exc:
            raise GeminiMalformedResponseError(
                f"Failed to parse model output text as JSON: {text_content[:200]}"
            ) from exc

        try:
            return model_cls.model_validate(parsed_json)
        except ValidationError as exc:
            raise GeminiMalformedResponseError(
                f"Gemini JSON output violated {schema_label}: {exc}"
            ) from exc

    # Keep legacy alias so existing test patches on `_parse_successful_response` continue to work
    def _parse_successful_response(self, raw_body: str) -> GeminiExtractionResponse:
        """Alias for _parse_extraction_response (backward-compatibility)."""
        return self._parse_extraction_response(raw_body)

    async def verify_connectivity(self) -> bool:
        """Verify API key validity against official endpoint.

        Performs a lightweight minimal request to verify authorization.
        Returns True if authorized, False otherwise. Never throws.
        """
        if not self.api_key:
            return False

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
            "User-Agent": "LeadForge/0.1.0",
        }
        # Lightweight ping: check model details via GET or minimal generateContent
        url = f"{GEMINI_API_BASE_URL}/{self.model}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers=headers)
                return res.status_code == 200
        except (httpx.RequestError, OSError):
            return False


def get_gemini_client() -> GeminiClient:
    """Factory function returning configured Gemini client instance."""
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
    )
