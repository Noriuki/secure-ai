from pathlib import Path


class LocalStorage:
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
        _ = metadata
        path = self._root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def read(self, key: str) -> bytes:
        path = self._root / key
        if not path.exists():
            raise FileNotFoundError(key)
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._root / key
        if path.exists():
            path.unlink()
