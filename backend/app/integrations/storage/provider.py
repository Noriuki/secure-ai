from app.integrations.storage.protocols import StoragePort
from app.integrations.storage.s3 import S3Storage


def get_storage() -> StoragePort:
    return S3Storage()
