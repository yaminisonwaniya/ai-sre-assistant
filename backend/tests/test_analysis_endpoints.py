"""Integration tests for requirement and project quality analysis endpoints."""

def test_analyze_single_requirement_endpoint(client):
    # 1. Create project & vague requirement statement
    proj_res = client.post("/api/v1/projects", json={"name": "Analysis Test Project"})
    proj_id = proj_res.json()["id"]

    req_payload = {
        "text": "The application should be user-friendly, fast, and easy to navigate.",
        "type": "UNCLASSIFIED"
    }
    create_res = client.post(f"/api/v1/projects/{proj_id}/requirements", json=req_payload)
    req_id = create_res.json()["id"]

    # 2. Trigger analysis endpoint
    analyze_res = client.post(f"/api/v1/requirements/{req_id}/analyze")
    assert analyze_res.status_code == 200
    analyzed = analyze_res.json()

    assert analyzed["id"] == req_id
    assert analyzed["status"] == "ANALYZED"
    assert analyzed["type"] == "NON_FUNCTIONAL"
    assert analyzed["quality_score"] < 80.0
    assert len(analyzed["issues"]) >= 2

    # Check issue attributes
    first_issue = analyzed["issues"][0]
    assert "category" in first_issue
    assert "severity" in first_issue
    assert "explanation" in first_issue
    assert first_issue["standard_reference"].startswith("ISO/IEC/IEEE 29148")


def test_analyze_project_requirements_batch_endpoint(client):
    proj_res = client.post("/api/v1/projects", json={"name": "Batch Analysis Project"})
    proj_id = proj_res.json()["id"]

    client.post(f"/api/v1/projects/{proj_id}/requirements", json={
        "text": "The system shall encrypt patient data at rest using AES-256."
    })
    client.post(f"/api/v1/projects/{proj_id}/requirements", json={
        "text": "The software should process records quickly."
    })

    # Trigger batch analysis
    batch_res = client.post(f"/api/v1/projects/{proj_id}/analyze")
    assert batch_res.status_code == 200
    items = batch_res.json()
    assert len(items) == 2
    assert all(item["status"] == "ANALYZED" for item in items)


def test_analyze_nonexistent_requirement_returns_404(client):
    res = client.post("/api/v1/requirements/999999/analyze")
    assert res.status_code == 404
