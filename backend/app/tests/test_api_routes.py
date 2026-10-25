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
