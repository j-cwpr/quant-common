"""Shared market data storage configuration."""

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class DataConfig:
    """Configuration shared by market data services."""

    storage_path: str = "data/market"

    @classmethod
    def from_env(cls) -> "DataConfig":
        return cls(storage_path=os.getenv("QUANT_MARKET_DATA_PATH", "data/market"))
