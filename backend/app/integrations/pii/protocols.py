from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID


@dataclass(slots=True)
class PiiMatch:
    token: str
    pii_type: str
    original_value: str
    start: int | None = None
    end: int | None = None


@dataclass(slots=True)
class AnonymizeResult:
    text: str
    matches: list[PiiMatch] = field(default_factory=list)


class PiiProcessor(Protocol):
    def anonymize(
        self,
        text: str,
        *,
        document_id: UUID | None = None,
    ) -> AnonymizeResult: ...
