"""In-memory registry for datasets loaded by instrument key."""

from quant_common.data.dataset import MarketDataset
from quant_common.data.instruments.base import Instrument


class InstrumentRegistry:
    """Stores the most recently loaded dataset for each instrument identity."""

    def __init__(self) -> None:
        self._datasets: dict[str, MarketDataset] = {}

    def register(self, instrument: Instrument, dataset: MarketDataset) -> None:
        if instrument.key != dataset.instrument_key:
            raise ValueError("Dataset instrument key does not match the instrument")
        self._datasets[instrument.key] = dataset

    def get(self, instrument: Instrument | str) -> MarketDataset:
        key = instrument if isinstance(instrument, str) else instrument.key
        return self._datasets[key]

    def keys(self) -> tuple[str, ...]:
        return tuple(self._datasets)

    def all(self) -> tuple[MarketDataset, ...]:
        return tuple(self._datasets.values())
