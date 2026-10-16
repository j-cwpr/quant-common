"""Loaded dataset container stored in the instrument registry."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MarketDataset:
    """A locally available instrument dataset and its requested coverage."""

    instrument_key: str
    start_date: date
    end_date: date
    files_by_data_type: dict[str, tuple[Path, ...]]

    @property
    def data_types(self) -> tuple[str, ...]:
        return tuple(self.files_by_data_type)
