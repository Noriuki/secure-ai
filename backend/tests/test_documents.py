from fastapi.testclient import TestClient


def _create_workspace(client: TestClient) -> str:
    response = client.post("/api/v1/workspaces", json={"name": "Docs WS"})
    assert response.status_code == 201
    return response.json()["id"]


def test_upload_list_and_delete_document(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.documents.service.start_knowledge_base_sync",
        lambda: "job-test-1",
    )
    workspace_id = _create_workspace(client)

    upload = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("nota.txt", b"hello secure ai", "text/plain")},
    )
    assert upload.status_code == 201
    document = upload.json()
    assert document["filename"] == "nota.txt"
    assert document["status"] == "ready"
    assert document["kb_sync_status"] == "started"
    assert document["kb_sync_job_id"] == "job-test-1"

    listed = client.get(f"/api/v1/workspaces/{workspace_id}/documents")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/v1/workspaces/{workspace_id}/documents/{document['id']}")
    assert deleted.status_code == 200

    listed_after = client.get(f"/api/v1/workspaces/{workspace_id}/documents")
    assert listed_after.json() == []


def test_upload_pdf_is_parsed(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.documents.service.start_knowledge_base_sync",
        lambda: None,
    )
    monkeypatch.setattr(
        "app.modules.documents.service.extract_text_from_pdf",
        lambda _data: "Contrato PDF com email teste@empresa.com",
    )
    workspace_id = _create_workspace(client)

    upload = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("contrato.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert upload.status_code == 201
    body = upload.json()
    assert body["filename"] == "contrato.pdf"
    assert body["content_type"] == "text/plain"
    assert body["storage_key"].endswith(".txt")
    assert body["kb_sync_status"] == "skipped"


def test_reject_unsupported_binary(client: TestClient) -> None:
    workspace_id = _create_workspace(client)
    upload = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents",
        files={"file": ("foto.png", b"\x89PNG", "image/png")},
    )
    assert upload.status_code == 422
