from __future__ import annotations

from uuid import UUID

import httpx

from app.core.config import get_settings
from app.integrations.pii.protocols import AnonymizeResult, PiiMatch


class PresidioPiiProcessor:
    _language = "pt"

    def __init__(self) -> None:
        settings = get_settings()
        self._analyzer_url = settings.presidio_analyzer_url.rstrip("/")
        self._timeout = settings.presidio_timeout_seconds

    def anonymize(
        self,
        text: str,
        *,
        document_id: UUID | None = None,
    ) -> AnonymizeResult:
        _ = document_id
        if not text.strip():
            return AnonymizeResult(text=text, matches=[])

        entities = self._dedupe_overlaps(self._analyze_text(text))
        matches: list[PiiMatch] = []
        anonymized = text
        counters: dict[str, int] = {}

        for entity in sorted(entities, key=lambda item: item["start"], reverse=True):
            start = int(entity["start"])
            end = int(entity["end"])
            if start < 0 or end > len(text) or start >= end:
                continue
            pii_type = str(entity["entity_type"])
            original = text[start:end]
            counters[pii_type] = counters.get(pii_type, 0) + 1
            token = f"{{{{PII_{pii_type}_{counters[pii_type]}}}}}"
            anonymized = anonymized[:start] + token + anonymized[end:]
            matches.append(
                PiiMatch(
                    token=token,
                    pii_type=pii_type,
                    original_value=original,
                    start=start,
                    end=end,
                )
            )

        matches.reverse()
        return AnonymizeResult(text=anonymized, matches=matches)

    def _analyze_text(self, text: str) -> list[dict]:
        url = f"{self._analyzer_url}/analyze"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    url,
                    json={"text": text, "language": self._language},
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Presidio Analyzer unreachable at {url}. "
                "Run: docker compose up -d --build presidio-analyzer"
            ) from exc

        if not isinstance(payload, list):
            raise RuntimeError("Presidio Analyzer returned unexpected payload")
        return payload

    @staticmethod
    def _dedupe_overlaps(entities: list[dict]) -> list[dict]:
        ordered = sorted(
            entities,
            key=lambda item: (int(item["start"]), -(int(item["end"]) - int(item["start"]))),
        )
        kept: list[dict] = []
        last_end = -1
        for entity in ordered:
            start = int(entity["start"])
            end = int(entity["end"])
            if start < last_end:
                continue
            kept.append(entity)
            last_end = end
        return kept
