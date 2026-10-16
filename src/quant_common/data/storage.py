"""Local storage for downloaded datasets."""

from pathlib import Path


class LocalStorage:
    @staticmethod
    def prepare(path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target
