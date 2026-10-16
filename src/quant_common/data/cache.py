"""Simple local cache paths for market data files."""

from datetime import date
from pathlib import Path


class DatasetCache:
    """Maps dataset identity to a stable local path."""

    def __init__(self, root: str | Path = "data/market") -> None:
        self.root = Path(root)

    def path_for(self, instrument_key: str, data_type: str, day: date) -> Path:
        key_path = Path(*instrument_key.split(":"))
        if any(part in {".", ".."} for part in key_path.parts):
            raise ValueError(f"Invalid instrument key: {instrument_key}")
        safe_data_type = data_type.replace("/", "-").replace(":", "-")
        return self.root / key_path / safe_data_type / f"{day:%Y-%m-%d}.csv.gz"
