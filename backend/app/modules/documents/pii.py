from uuid import UUID

from sqlalchemy.orm import Session

from app.integrations.pii.protocols import AnonymizeResult, PiiMatch, PiiProcessor
from app.modules.documents.models import PiiVaultEntry
from app.shared.schemas import TimestampMixin


def save_vault_matches(
    db: Session,
    document_id: UUID,
    matches: list[PiiMatch],
) -> None:
    if not matches:
        return

    now = TimestampMixin.utcnow()
    db.add_all(
        [
            PiiVaultEntry(
                document_id=document_id,
                token=match.token,
                pii_type=match.pii_type,
                original_value=match.original_value,
                created_at=now,
            )
            for match in matches
        ]
    )
    db.commit()


def anonymize_text(
    processor: PiiProcessor,
    text: str,
    *,
    document_id: UUID | None = None,
) -> AnonymizeResult:
    return processor.anonymize(text, document_id=document_id)
