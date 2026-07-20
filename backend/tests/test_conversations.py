from fastapi.testclient import TestClient


def _create_workspace(client: TestClient) -> str:
    response = client.post("/api/v1/workspaces", json={"name": "Chat WS"})
    assert response.status_code == 201
    return response.json()["id"]


def test_conversation_and_chat(client: TestClient) -> None:
    workspace_id = _create_workspace(client)

    created = client.post(
        f"/api/v1/workspaces/{workspace_id}/conversations",
        json={"title": "Onboarding"},
    )
    assert created.status_code == 201
    conversation_id = created.json()["id"]

    chat = client.post(
        f"/api/v1/workspaces/{workspace_id}/conversations/{conversation_id}/messages",
        json={"content": "Como subo a API?"},
    )
    assert chat.status_code == 201
    body = chat.json()
    assert body["user_message"]["role"] == "user"
    assert body["assistant_message"]["role"] == "assistant"
    assert "[test]" in body["assistant_message"]["content"]
    assert body["assistant_message"]["sources"]
    assert body["assistant_message"]["sources"][0]["title"] == "guia.txt"

    messages = client.get(
        f"/api/v1/workspaces/{workspace_id}/conversations/{conversation_id}/messages",
    )
    assert messages.status_code == 200
    assert len(messages.json()) == 2

    dashboard = client.get("/api/v1/dashboard")
    assert dashboard.status_code == 200
    stats = dashboard.json()
    assert stats["llm_calls"] >= 1
    assert stats["avg_latency_ms"] is not None
    assert any(event["event_type"] == "chat" for event in stats["recent_events"])
