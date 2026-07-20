"""Amazon Bedrock Managed Knowledge Base RAG (AgenticRetrieveStream)."""

from __future__ import annotations

import time
from uuid import UUID

import boto3

from app.core.config import get_settings
from app.integrations.bedrock.protocols import RagReply, RagSource


class BedrockRag:
    """RAG against a Managed Knowledge Base via AgenticRetrieveStream.

    Classic RetrieveAndGenerate is not supported for managed KBs.
    Managed store filters do not support STRING_CONTAINS on S3 paths, and custom
    S3 object metadata is not exposed as filter attributes — so workspace
    isolation is enforced by post-filtering retrieved chunks on
    `workspaces/{workspace_id}/` in `_source_uri` / `_document_id`.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._kb_id = settings.bedrock_knowledge_base_id
        self._region = settings.aws_region
        self._model_id = settings.bedrock_model_id
        if not self._kb_id:
            raise RuntimeError(
                "BEDROCK_KNOWLEDGE_BASE_ID is required. "
                "Create the Knowledge Base on AWS and set it in .env.",
            )
        self._client = boto3.client("bedrock-agent-runtime", region_name=self._region)

    def ask(self, *, workspace_id: UUID, question: str) -> RagReply:
        workspace = str(workspace_id)
        path_marker = f"workspaces/{workspace}/"
        started = time.perf_counter()
        response = self._client.agentic_retrieve_stream(
            messages=[{"role": "user", "content": {"text": question}}],
            retrievers=[
                {
                    "description": "SecureAI workspace documents",
                    "configuration": {
                        "knowledgeBase": {
                            "knowledgeBaseId": self._kb_id,
                            "retrievalOverrides": {"maxNumberOfResults": 10},
                        }
                    },
                }
            ],
            agenticRetrieveConfiguration={
                "foundationModelType": "MANAGED",
                "rerankingModelType": "NONE",
                "maxAgentIteration": 3,
            },
            generateResponse=True,
        )

        answer_parts: list[str] = []
        answer = ""
        sources: list[RagSource] = []

        for event in response.get("stream", []):
            if "responseEvent" in event:
                text = event["responseEvent"].get("text")
                if text:
                    answer_parts.append(text)
            elif "result" in event:
                result = event["result"]
                generated = result.get("generatedResponse") or {}
                if generated.get("answer"):
                    answer = generated["answer"]
                for item in result.get("results") or []:
                    if not self._belongs_to_workspace(item, path_marker):
                        continue
                    sources.append(self._source_from_result(item))
            elif any(key.endswith("Exception") for key in event):
                exc_payload = next(v for k, v in event.items() if k.endswith("Exception"))
                message = (
                    (exc_payload or {}).get("message")
                    if isinstance(exc_payload, dict)
                    else str(exc_payload)
                )
                raise RuntimeError(f"Bedrock AgenticRetrieveStream failed: {message}")

        if not answer and answer_parts:
            answer = "".join(answer_parts)

        if not sources:
            answer = (
                "Ainda não encontrei trechos indexados deste workspace. "
                "Se o documento acabou de ser enviado, aguarde a indexação da "
                "Knowledge Base (geralmente 1–3 min) e pergunte de novo."
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        return RagReply(
            answer=answer,
            sources=sources,
            model=self._model_id or "managed",
            latency_ms=latency_ms,
        )

    @staticmethod
    def _belongs_to_workspace(item: dict, path_marker: str) -> bool:
        metadata = item.get("metadata") or {}
        haystacks = (
            str(metadata.get("_source_uri") or ""),
            str(metadata.get("_document_id") or ""),
            str(metadata.get("x-amz-bedrock-kb-source-uri") or ""),
            str(metadata.get("sourceUri") or ""),
            str(metadata.get("uri") or ""),
        )
        return any(path_marker in value for value in haystacks)

    @staticmethod
    def _source_from_result(item: dict) -> RagSource:
        content = item.get("content") or {}
        metadata = item.get("metadata") or {}
        text = content.get("text")
        uri = (
            metadata.get("_source_uri")
            or metadata.get("_document_id")
            or metadata.get("x-amz-bedrock-kb-source-uri")
            or metadata.get("sourceUri")
            or metadata.get("uri")
        )
        title = (
            metadata.get("_document_title")
            or metadata.get("filename")
            or metadata.get("x-amz-meta-filename")
            or (str(uri) if uri else "source")
        )
        title_str = str(title)
        if "/" in title_str:
            title_str = title_str.rstrip("/").rsplit("/", 1)[-1]
        return RagSource(
            title=title_str,
            excerpt=text if isinstance(text, str) else None,
            uri=str(uri) if uri else None,
            score=None,
        )
