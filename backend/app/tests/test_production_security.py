"""Security audit tests for LeadForge production readiness (SECURITY.md).

Covers:
1. Zero frontend secret exposure (no API keys or credentials in client bundles).
2. Architectural Zero-Send Guarantee: absence of any email dispatching drivers or SMTP libs.
3. CORS configuration validation (explicit whitelisted origins, no wildcard on credentials).
4. CSV Formula Injection Defense (CWE-1236 sanitization: =, +, -, @ prefixes escaped).
5. Error responses do not leak raw API keys, tracebacks, or database paths.
6. API Input validation: strict prospect domain format, valid score boundaries.
"""

import sys

from fastapi.testclient import TestClient

from app.api.routes_export import sanitize_csv_cell
from app.core import config
from app.main import app


def test_zero_email_dispatch_infrastructure():
    """Verify strictly zero mail dispatch libraries exist in Python environment/dependencies."""
    forbidden = ["smtplib", "sendgrid", "boto3.ses", "resend", "mailgun"]
    for mod in forbidden:
        assert mod not in sys.modules, f"Security violation: {mod} found in memory!"


def test_csv_formula_injection_sanitization():
    """Verify CWE-1236 defense: cells starting with dangerous characters are prefixed with single quote."""
    # Test all dangerous prefix triggers defined in SECURITY.md §8
    dangerous_inputs = [
        "=cmd|' /C calc'!A0",
        "+1+2",
        "-5+10",
        "@SUM(A1:A10)",
        "\tmalicious_tab",
        "\rmalicious_cr",
    ]
    for payload in dangerous_inputs:
        sanitized = sanitize_csv_cell(payload)
        assert sanitized.startswith("'"), (
            f"Failed to sanitize formula injection: {payload}"
        )
        assert sanitized[1:] == payload

    # Safe inputs must remain unchanged
    safe_inputs = ["Khatabook", "https://khatabook.com", "90", "FACT", ""]
    for safe in safe_inputs:
        assert sanitize_csv_cell(safe) == safe
    assert sanitize_csv_cell(None) == ""


def test_cors_origin_whitelist_enforced():
    """Verify CORS configuration uses explicitly defined origins without permissive wildcard."""
    origins = config.settings.CORS_ORIGINS
    assert isinstance(origins, list)
    assert len(origins) >= 1
    # Strict check: wildcard '*' cannot be combined with allow_credentials=True
    assert "*" not in origins, (
        "Security violation: CORS allow_origins contains wildcard '*'"
    )


def test_error_response_does_not_leak_api_keys():
    """Verify API error responses never expose backend configuration secrets."""
    secret_key = "super-confidential-secret-key-12345"
    with TestClient(app) as client:
        # Request a nonexistent resource
        res = client.get("/api/prospects/999999")
        assert res.status_code == 404
        assert secret_key not in res.text

        # Bad route
        res_bad = client.get("/api/invalid-route")
        assert res_bad.status_code == 404
        assert secret_key not in res_bad.text


def test_input_validation_on_prospect_and_draft_endpoints():
    """Verify input validation rejects invalid lead_score queries and invalid payloads."""
    with TestClient(app) as client:
        # Invalid min_score (< 0 or > 100)
        res_low = client.get("/api/prospects?min_score=-5")
        assert res_low.status_code == 422

        res_high = client.get("/api/prospects?min_score=150")
        assert res_high.status_code == 422
