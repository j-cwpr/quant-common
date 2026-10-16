"""Common interface implemented by market data providers."""

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Any

from quant_common.data.instruments.base import Instrument


class MarketDataProvider(ABC):
    """One source that can retrieve one or more kinds of instrument data."""

    name: str

    @abstractmethod
    def supports(self, instrument: Instrument, data_type: str) -> bool:
        """Return whether this provider can serve the requested data."""

    @abstractmethod
    def download_dataset(
        self,
        *,
        exchange: str,
        data_type: str,
        symbol: str,
        day: date,
        destination: Path,
    ) -> Path:
        """Download a single day's dataset to the requested local path."""

    def list_instruments(self, exchange: str) -> list[dict[str, Any]]:
        """Return vendor metadata when the provider supports instrument discovery."""
        return []
