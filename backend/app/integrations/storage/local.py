from pathlib import Path


class LocalStorage:
    """Test/local disk adapter — used via dependency override in tests."""

    def __init__(self, root: str | Path | None = None) -> None:
        self._root = Path(root or "./storage").resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        key: str,
        data: bytes,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        _ = metadata  # local disk ignores object metadata
        path = self._root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def delete(self, key: str) -> None:
        path = self._root / key
        if path.exists():
            path.unlink()

    def exists(self, key: str) -> bool:
        return (self._root / key).exists()
