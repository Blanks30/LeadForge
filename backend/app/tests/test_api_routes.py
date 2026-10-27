"""Integration tests for all LeadForge REST API endpoints."""

from fastapi.testclient import TestClient

from app.main import app


def test_api_health_ok():
    """Verify GET /api/health returns operational status."""
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "db": True}


def test_get_and_update_icp():
    """Verify GET and POST /api/icp endpoints."""
    with TestClient(app) as client:
        # GET ICP
        get_res = client.get("/api/icp")
        assert get_res.status_code == 200
        data = get_res.json()
        assert data["target_geo"] == "India"
        assert len(data["smb_criteria"]) >= 1

        # POST Update ICP
        update_payload = {
            "vertical": "Indian SMB FinTech & ERP",
            "smb_criteria": ["Mobile-first WhatsApp invoicing", "UPI payments"],
        }
        update_res = client.post("/api/icp", json=update_payload)
        assert update_res.status_code == 200
        updated_data = update_res.json()
        assert updated_data["vertical"] == "Indian SMB FinTech & ERP"
        assert updated_data["smb_criteria"] == [
            "Mobile-first WhatsApp invoicing",
            "UPI payments",
        ]


def test_list_and_seed_prospects():
    """Verify POST /api/prospects/seed and GET /api/prospects."""
    with TestClient(app) as client:
        seed_res = client.post("/api/prospects/seed")
        assert seed_res.status_code == 200
        prospects = seed_res.json()
        assert len(prospects) == 10

        # Query list with search filter
        list_res = client.get("/api/prospects?search=Khatabook")
        assert list_res.status_code == 200
        filtered = list_res.json()
        assert len(filtered) == 1
        assert filtered[0]["company_name"] == "Khatabook"


def test_prospect_detail_and_research_flow():
    """Verify GET /api/prospects/{id} and POST /api/prospects/{id}/research."""
    with TestClient(app) as client:
        # Get first prospect
        list_res = client.get("/api/prospects?search=Khatabook")
        prospect_id = list_res.json()[0]["id"]

        # Trigger research
        research_res = client.post(f"/api/prospects/{prospect_id}/research")
        assert research_res.status_code == 200
        analyzed = research_res.json()

        assert analyzed["status"] == "ANALYZED"
        assert analyzed["lead_score"] > 0
        assert analyzed["score_breakdown"] is not None
        assert analyzed["score_breakdown"]["total"] == analyzed["lead_score"]
        assert len(analyzed["web_sources"]) >= 1
        assert len(analyzed["evidence_items"]) >= 1

        # Verify full detail endpoint returns evidence
        detail_res = client.get(f"/api/prospects/{prospect_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["lead_score"] == analyzed["lead_score"]


def test_create_outreach_draft_flow():
    """Verify POST /api/prospects/{id}/draft generates grounded cold email."""
    with TestClient(app) as client:
        # Research Khatabook first
        list_res = client.get("/api/prospects?search=Khatabook")
        prospect_id = list_res.json()[0]["id"]
        client.post(f"/api/prospects/{prospect_id}/research")

        # Create draft
        draft_res = client.post(
            f"/api/prospects/{prospect_id}/draft",
            json={
                "template_type": "EVIDENCE_PROBLEM_SOLUTION",
                "tone": "CONSULTATIVE_DIRECT",
            },
        )
        assert draft_res.status_code == 200
        draft = draft_res.json()

        assert draft["subject_line"] != ""
        assert "[Ref: #" in draft["body_text"]
        assert len(draft["citations"]) >= 1


def test_export_csv_endpoint():
    """Verify GET /api/export/csv returns valid CSV attachment."""
    with TestClient(app) as client:
        res = client.get("/api/export/csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "leadforge_prospects.csv" in res.headers["content-disposition"]
        csv_text = res.text
        assert "Company Name,Website Domain,Lead Score" in csv_text
        assert "Khatabook" in csv_text


def test_nonexistent_prospect_returns_404():
    """Verify 404 response on missing prospect ID."""
    with TestClient(app) as client:
        res = client.get("/api/prospects/99999")
        assert res.status_code == 404
        post_res = client.post("/api/prospects/99999/research")
        assert post_res.status_code == 404


def test_multi_prospect_independent_research():
    """Verify multiple prospects can be researched independently without artificial limits."""
    with TestClient(app) as client:
        # Seed prospects to ensure standard test catalog
        client.post("/api/prospects/seed")

        # Fetch list and verify at least 3 prospects exist
        list_res = client.get("/api/prospects")
        assert list_res.status_code == 200
        prospects = list_res.json()
        assert len(prospects) >= 3

        test_domains = ["khatabook.com", "mydukaan.io", "shiprocket.in"]
        researched_results = []

        for domain in test_domains:
            prospect = next(p for p in prospects if p["domain"] == domain)
            res = client.post(f"/api/prospects/{prospect['id']}/research")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ANALYZED"
            assert data["domain"] == domain
            assert data["lead_score"] > 0
            assert data["score_breakdown"] is not None
            assert len(data["evidence_items"]) > 0
            researched_results.append(data)

        # Verify results retain distinct identities, scores, and domains
        domains_seen = {r["domain"] for r in researched_results}
        assert domains_seen == set(test_domains)

        # Verify GET /api/prospects preserves score_breakdown on summary objects
        summary_res = client.get("/api/prospects")
        assert summary_res.status_code == 200
        all_summaries = summary_res.json()
        for domain in test_domains:
            summary_item = next(p for p in all_summaries if p["domain"] == domain)
            assert summary_item["status"] == "ANALYZED"
            assert summary_item["score_breakdown"] is not None
            assert "total" in summary_item["score_breakdown"]


def test_research_failure_persists_status_and_allows_retry(monkeypatch):
    """Verify that a crawler failure persists status=FAILED, returns 502, and can be retried."""
    from app.services import research_service, tinyfish_client

    with TestClient(app) as client:
        client.post("/api/prospects/seed")
        list_res = client.get("/api/prospects?search=Vyapar")
        vyapar_id = list_res.json()[0]["id"]

        # 1. Simulate crawler returning None (upstream crawl failure)
        class FailingCrawler(tinyfish_client.TinyFishClientBase):
            async def crawl_prospect(self, domain: str, website_url: str):
                return None

        monkeypatch.setattr(research_service, "get_tinyfish_client", lambda: FailingCrawler())

        fail_res = client.post(f"/api/prospects/{vyapar_id}/research")
        assert fail_res.status_code == 502
        assert "failed" in fail_res.json()["detail"].lower()

        # Check that prospect status in DB is now FAILED, not indefinitely PENDING
        detail_res = client.get(f"/api/prospects/{vyapar_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["status"] == "FAILED"

        # 2. Restore normal crawler (mock) and verify retry succeeds
        monkeypatch.undo()
        retry_res = client.post(f"/api/prospects/{vyapar_id}/research")
        assert retry_res.status_code == 200
        retried_data = retry_res.json()
        assert retried_data["status"] == "ANALYZED"
        assert retried_data["lead_score"] > 0

