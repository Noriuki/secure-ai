from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID


@dataclass(slots=True)
class RagSource:
    title: str
    excerpt: str | None = None
    uri: str | None = None
    score: float | None = None


@dataclass(slots=True)
class RagReply:
    answer: str
    sources: list[RagSource] = field(default_factory=list)
    latency_ms: int | None = None


class RagPort(Protocol):
    def ask(self, *, workspace_id: UUID, question: str) -> RagReply: ...
