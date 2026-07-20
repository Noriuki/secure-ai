from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security.repository import PiiVaultRepository
from app.integrations.pii.protocols import AnonymizeResult, PiiProcessor
from app.integrations.pii.provider import get_pii_processor


class PiiService:
    def __init__(self, repository: PiiVaultRepository, processor: PiiProcessor) -> None:
        self._repository = repository
        self._processor = processor

    def anonymize_and_vault(
        self,
        text: str,
        *,
        document_id: UUID | None = None,
    ) -> AnonymizeResult:
        result = self._processor.anonymize(text, document_id=document_id)
        if result.matches:
            self._repository.save_matches(document_id, result.matches)
        return result


def get_pii_service(
    db: Annotated[Session, Depends(get_db)],
    processor: Annotated[PiiProcessor, Depends(get_pii_processor)],
) -> PiiService:
    return PiiService(PiiVaultRepository(db), processor)
