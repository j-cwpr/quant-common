"""Base instrument model."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Instrument:
    exchange: str
    symbol: str
    base_asset: str | None = None
    quote_asset: str | None = None
    instrument_type: ClassVar[str] = "instrument"

    @property
    def key(self) -> str:
        """Stable, readable registry key for this instrument."""
        return f"{self.instrument_type}:{self.exchange.strip().lower()}:{self.symbol.strip().upper()}"
