"""Tests for Project CRUD REST endpoints."""

def test_list_projects_empty(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_create_and_get_project(client):
    # 1. Create project
    payload = {
        "name": "E-Commerce System SRS",
        "description": "Software Requirements Specification for online retail platform."
    }
    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] is not None
    assert created["name"] == payload["name"]
    assert created["requirement_count"] == 0
    project_id = created["id"]

    # 2. Fetch project details
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["id"] == project_id
    assert fetched["name"] == payload["name"]
    assert fetched["requirements"] == []


def test_update_project(client):
    # Create initial project
    create_res = client.post("/api/v1/projects", json={"name": "Initial Project Name"})
    project_id = create_res.json()["id"]

    # Update title
    update_payload = {"name": "Updated Project Name", "description": "New description added"}
    update_res = client.put(f"/api/v1/projects/{project_id}", json=update_payload)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Updated Project Name"
    assert updated["description"] == "New description added"


def test_delete_project(client):
    # Create project
    create_res = client.post("/api/v1/projects", json={"name": "Temporary Project"})
    project_id = create_res.json()["id"]

    # Delete project
    delete_res = client.delete(f"/api/v1/projects/{project_id}")
    assert delete_res.status_code == 204

    # Verify 404 on get
    get_res = client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 404


def test_get_nonexistent_project_returns_404(client):
    response = client.get("/api/v1/projects/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
