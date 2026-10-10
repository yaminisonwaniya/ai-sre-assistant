"""Tests for Requirement CRUD REST endpoints, filtering, and validation."""

def test_create_and_list_requirements(client):
    # 1. Create project
    proj_res = client.post("/api/v1/projects", json={"name": "Banking SRS"})
    proj_id = proj_res.json()["id"]

    # 2. Add requirement with auto-generated code
    req_payload = {
        "text": "The system shall process funds transfers between accounts within 500ms.",
        "type": "FUNCTIONAL",
        "subtype": "PAYMENTS",
        "quality_score": 90.0,
        "status": "DRAFT"
    }
    create_res = client.post(f"/api/v1/projects/{proj_id}/requirements", json=req_payload)
    assert create_res.status_code == 201
    created_req = create_res.json()
    assert created_req["id"] is not None
    assert created_req["req_code"] == "REQ-001"
    assert created_req["text"] == req_payload["text"]

    # 3. Add second requirement
    req2_payload = {
        "text": "The system shall log all transaction attempts for audit compliance.",
        "type": "NON_FUNCTIONAL",
        "subtype": "SECURITY",
        "quality_score": 95.0,
        "status": "APPROVED"
    }
    create_res2 = client.post(f"/api/v1/projects/{proj_id}/requirements", json=req2_payload)
    assert create_res2.status_code == 201
    assert create_res2.json()["req_code"] == "REQ-002"

    # 4. List project requirements
    list_res = client.get(f"/api/v1/projects/{proj_id}/requirements")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_filter_requirements_by_type_and_status(client):
    proj_res = client.post("/api/v1/projects", json={"name": "Filter Test Project"})
    proj_id = proj_res.json()["id"]

    client.post(f"/api/v1/projects/{proj_id}/requirements", json={
        "text": "Functional requirement 1",
        "type": "FUNCTIONAL",
        "status": "DRAFT"
    })
    client.post(f"/api/v1/projects/{proj_id}/requirements", json={
        "text": "Non-functional requirement 1",
        "type": "NON_FUNCTIONAL",
        "status": "APPROVED"
    })

    # Filter by type=FUNCTIONAL
    func_res = client.get(f"/api/v1/projects/{proj_id}/requirements?req_type=FUNCTIONAL")
    assert func_res.status_code == 200
    assert func_res.json()["total"] == 1
    assert func_res.json()["items"][0]["type"] == "FUNCTIONAL"

    # Filter by status=APPROVED
    app_res = client.get(f"/api/v1/projects/{proj_id}/requirements?status=APPROVED")
    assert app_res.status_code == 200
    assert app_res.json()["total"] == 1
    assert app_res.json()["items"][0]["status"] == "APPROVED"


def test_update_and_delete_requirement(client):
    proj_res = client.post("/api/v1/projects", json={"name": "Edit Req Project"})
    proj_id = proj_res.json()["id"]

    req_res = client.post(f"/api/v1/projects/{proj_id}/requirements", json={
        "text": "Original requirement statement."
    })
    req_id = req_res.json()["id"]

    # Update requirement
    update_res = client.put(f"/api/v1/requirements/{req_id}", json={
        "text": "Updated and clarified requirement statement.",
        "quality_score": 88.0,
        "status": "REVIEWED"
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["text"] == "Updated and clarified requirement statement."
    assert updated["status"] == "REVIEWED"

    # Delete requirement
    del_res = client.delete(f"/api/v1/requirements/{req_id}")
    assert del_res.status_code == 204

    # Verify 404
    get_res = client.get(f"/api/v1/requirements/{req_id}")
    assert get_res.status_code == 404


def test_requirement_edge_cases(client):
    # Create for non-existent project returns 404
    res = client.post("/api/v1/projects/99999/requirements", json={"text": "Orphan requirement"})
    assert res.status_code == 404

    # Empty requirement text validation
    proj_res = client.post("/api/v1/projects", json={"name": "Validation Project"})
    proj_id = proj_res.json()["id"]
    val_res = client.post(f"/api/v1/projects/{proj_id}/requirements", json={"text": ""})
    assert val_res.status_code == 422  # Unprocessable Entity
