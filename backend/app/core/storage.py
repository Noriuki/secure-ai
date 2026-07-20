"""Re-exports storage port + factory for app modules."""

from app.integrations.storage.local import LocalStorage
from app.integrations.storage.protocols import StoragePort
from app.integrations.storage.provider import get_storage

__all__ = ["LocalStorage", "StoragePort", "get_storage"]
