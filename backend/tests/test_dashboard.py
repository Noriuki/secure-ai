from fastapi.testclient import TestClient


def test_dashboard_empty(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["workspaces"] == 0
    assert body["documents"] == 0
    assert body["llm_calls"] == 0
    assert body["recent_events"] == []
