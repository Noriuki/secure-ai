from fastapi.testclient import TestClient


def test_create_and_list_workspaces(client: TestClient) -> None:
    create = client.post(
        "/api/v1/workspaces",
        json={"name": "Onboarding", "description": "Docs internos"},
    )
    assert create.status_code == 201
    workspace = create.json()
    assert workspace["name"] == "Onboarding"
    assert "id" in workspace

    listed = client.get("/api/v1/workspaces")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_get_workspace_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/workspaces/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_and_delete_workspace(client: TestClient) -> None:
    created = client.post("/api/v1/workspaces", json={"name": "Draft"}).json()
    workspace_id = created["id"]

    updated = client.patch(f"/api/v1/workspaces/{workspace_id}", json={"name": "Final"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Final"

    deleted = client.delete(f"/api/v1/workspaces/{workspace_id}")
    assert deleted.status_code == 200

    missing = client.get(f"/api/v1/workspaces/{workspace_id}")
    assert missing.status_code == 404
