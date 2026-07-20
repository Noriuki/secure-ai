from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        default="application/octet-stream",
    )
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="uploaded")
    kb_sync_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    kb_sync_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )


class PiiVaultEntry(Base):
    """Token map persisted during document upload (no product rehydration)."""

    __tablename__ = "pii_vault_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    pii_type: Mapped[str] = mapped_column(String(64), nullable=False)
    original_value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
