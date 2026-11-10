"""Tests for custom company addition, validation, and research workflows."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_create_custom_prospect_success():
    """Verify successful creation of a custom company with 201 Created."""
    with TestClient(app) as client:
        # Seed initial data first so ICP exists
        client.post("/api/prospects/seed")

        payload = {
            "company_name": "Zoho Books",
            "website_url": "https://www.zohobooks.com",
            "description": "Cloud accounting software built for Indian businesses",
        }
        res = client.post("/api/prospects", json=payload)
        assert res.status_code == 201
        data = res.json()

        assert data["company_name"] == "Zoho Books"
        assert data["website_url"] == "https://www.zohobooks.com"
        assert data["domain"] == "zohobooks.com"
        assert data["status"] == "PENDING"
        assert data["lead_score"] == 0
        assert data["id"] is not None


def test_create_custom_prospect_missing_company_name():
    """Verify that an empty or missing company name returns 422."""
    with TestClient(app) as client:
        # Missing company_name
        res1 = client.post(
            "/api/prospects",
            json={"website_url": "https://example.com"},
        )
        assert res1.status_code == 422

        # Whitespace-only company_name
        res2 = client.post(
            "/api/prospects",
            json={"company_name": "   ", "website_url": "https://example.com"},
        )
        assert res2.status_code == 422


def test_create_custom_prospect_invalid_url():
    """Verify that an invalid URL returns 422."""
    with TestClient(app) as client:
        res = client.post(
            "/api/prospects",
            json={"company_name": "Bad URL Corp", "website_url": "not-a-valid-url"},
        )
        assert res.status_code == 422


def test_create_custom_prospect_unsupported_protocol():
    """Verify that non-HTTP/HTTPS protocols return 422."""
    with TestClient(app) as client:
        res = client.post(
            "/api/prospects",
            json={"company_name": "FTP SaaS", "website_url": "ftp://files.example.com"},
        )
        assert res.status_code == 422


def test_create_custom_prospect_duplicate_domain():
    """Verify that attempting to add an existing domain returns 409 Conflict."""
    with TestClient(app) as client:
        client.post("/api/prospects/seed")

        # Khatabook already exists in seeded catalog
        res1 = client.post(
            "/api/prospects",
            json={
                "company_name": "Khatabook Duplicate",
                "website_url": "https://khatabook.com",
            },
        )
        assert res1.status_code == 409
        assert "already exists" in res1.json()["detail"]

        # Also test www. variation of the same domain
        res2 = client.post(
            "/api/prospects",
            json={
                "company_name": "Khatabook WWW Duplicate",
                "website_url": "https://www.khatabook.com/pricing",
            },
        )
        assert res2.status_code == 409
        assert "already exists" in res2.json()["detail"]


def test_custom_prospect_appears_in_listing():
    """Verify that newly created custom prospect appears in GET /api/prospects."""
    with TestClient(app) as client:
        client.post("/api/prospects/seed")

        create_res = client.post(
            "/api/prospects",
            json={
                "company_name": "ClearTax Test Listing",
                "website_url": "https://cleartax.in",
            },
        )
        assert create_res.status_code == 201
        created_id = create_res.json()["id"]

        # Search for it in prospects listing
        list_res = client.get("/api/prospects?search=cleartax")
        assert list_res.status_code == 200
        items = list_res.json()
        assert any(item["id"] == created_id for item in items)


def test_research_endpoint_accepts_custom_prospect():
    """Verify that POST /api/prospects/{id}/research processes custom companies."""
    with TestClient(app) as client:
        client.post("/api/prospects/seed")

        create_res = client.post(
            "/api/prospects",
            json={
                "company_name": "Deskera Cloud",
                "website_url": "https://deskera.com",
            },
        )
        assert create_res.status_code == 201
        prospect_id = create_res.json()["id"]

        # Trigger research on the newly created custom company
        research_res = client.post(f"/api/prospects/{prospect_id}/research")
        assert research_res.status_code == 200
        analyzed = research_res.json()

        assert analyzed["id"] == prospect_id
        assert analyzed["status"] == "ANALYZED"
        assert analyzed["lead_score"] > 0
        assert len(analyzed["web_sources"]) >= 1
        assert len(analyzed["evidence_items"]) >= 1


def test_research_failure_preserves_company_and_retry():
    """Verify that crawl failure marks status FAILED, preserves company, and supports retry."""
    with TestClient(app) as client:
        client.post("/api/prospects/seed")

        create_res = client.post(
            "/api/prospects",
            json={
                "company_name": "Failing SaaS Co",
                "website_url": "https://failing-saas.co",
            },
        )
        assert create_res.status_code == 201
        prospect_id = create_res.json()["id"]

        # Mock crawler to fail by returning None
        with patch(
            "app.services.research_service.get_tinyfish_client"
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.crawl_prospect.return_value = None
            mock_get_client.return_value = mock_client

            fail_res = client.post(f"/api/prospects/{prospect_id}/research")
            # 502 Bad Gateway is returned when crawling fails
            assert fail_res.status_code == 502

        # Verify company is preserved in DB with FAILED status
        detail_res = client.get(f"/api/prospects/{prospect_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["status"] == "FAILED"
        assert detail_res.json()["company_name"] == "Failing SaaS Co"

        # Now test retry: run research without failure mock
        retry_res = client.post(f"/api/prospects/{prospect_id}/research")
        assert retry_res.status_code == 200
        retried = retry_res.json()
        assert retried["status"] == "ANALYZED"
        assert retried["lead_score"] > 0


def test_seeded_prospects_remain_intact():
    """Verify that adding custom prospects does not alter or corrupt the 10 seeded prospects."""
    with TestClient(app) as client:
        seed_res = client.post("/api/prospects/seed")
        assert seed_res.status_code == 200
        initial_prospects = seed_res.json()
        assert len(initial_prospects) == 10
        initial_domains = {p["domain"] for p in initial_prospects}

        # Add custom prospect
        client.post(
            "/api/prospects",
            json={
                "company_name": "Intact Check SaaS",
                "website_url": "https://intact-check.in",
            },
        )

        # Check all prospects
        all_res = client.get("/api/prospects")
        assert all_res.status_code == 200
        current_prospects = all_res.json()
        assert len(current_prospects) == 11

        current_domains = {p["domain"] for p in current_prospects}
        # All original 10 domains must still be present
        assert initial_domains.issubset(current_domains)
