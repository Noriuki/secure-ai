from collections.abc import Generator
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.db import Base, get_db
from app.core.security import models as _pii_models  # noqa: F401
from app.core.storage import LocalStorage, get_storage
from app.integrations.bedrock.protocols import RagPort, RagReply, RagSource
from app.integrations.bedrock.provider import get_rag
from app.integrations.pii.protocols import AnonymizeResult, PiiProcessor
from app.integrations.pii.provider import get_pii_processor
from app.main import create_app

# Import models so metadata is registered.
from app.modules.audit import models as _audit_models  # noqa: F401
from app.modules.conversations import models as _conversations_models  # noqa: F401
from app.modules.documents import models as _documents_models  # noqa: F401
from app.modules.workspaces import models as _workspaces_models  # noqa: F401

get_settings.cache_clear()


class _TestRag:
    def ask(self, *, workspace_id: UUID, question: str) -> RagReply:
        return RagReply(
            answer=f"[test] workspace={workspace_id} q={question}",
            sources=[
                RagSource(title="guia.txt", excerpt="subir a API", uri=None, score=0.9),
            ],
            model="test",
            latency_ms=12,
        )


class _TestPii:
    def anonymize(
        self,
        text: str,
        *,
        document_id: UUID | None = None,
    ) -> AnonymizeResult:
        _ = document_id
        return AnonymizeResult(text=text, matches=[])


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    return tmp_path / "storage"


@pytest.fixture
def client(db_session: Session, storage_dir: Path) -> Generator[TestClient, None, None]:
    get_settings.cache_clear()
    app = create_app()
    storage = LocalStorage(root=storage_dir)
    test_rag: RagPort = _TestRag()
    test_pii: PiiProcessor = _TestPii()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = lambda: storage
    app.dependency_overrides[get_rag] = lambda: test_rag
    app.dependency_overrides[get_pii_processor] = lambda: test_pii

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()
