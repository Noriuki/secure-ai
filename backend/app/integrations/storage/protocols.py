from typing import Protocol


class StoragePort(Protocol):
    def save(
        self,
        key: str,
        data: bytes,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str: ...

    def read(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None: ...
