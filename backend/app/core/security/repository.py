from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security.models import PiiVaultEntry
from app.integrations.pii.protocols import PiiMatch
from app.shared.schemas import TimestampMixin


class PiiVaultRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save_matches(
        self,
        document_id: UUID | None,
        matches: list[PiiMatch],
    ) -> list[PiiVaultEntry]:
        if not matches:
            return []

        now = TimestampMixin.utcnow()
        entries = [
            PiiVaultEntry(
                document_id=document_id,
                token=match.token,
                pii_type=match.pii_type,
                original_value=match.original_value,
                created_at=now,
            )
            for match in matches
        ]
        self._db.add_all(entries)
        self._db.commit()
        for entry in entries:
            self._db.refresh(entry)
        return entries

    def list_by_document(self, document_id: UUID) -> list[PiiVaultEntry]:
        stmt = select(PiiVaultEntry).where(PiiVaultEntry.document_id == document_id)
        return list(self._db.scalars(stmt).all())
