"""Market data orchestration and explicit per-instrument loading paths."""

from collections.abc import Sequence
from datetime import date
from pathlib import Path

from quant_common.data.config import DataConfig
from quant_common.data.dataset import MarketDataset
from quant_common.data.instruments.base import Instrument
from quant_common.data.instruments.perpetual_future.instrument import PerpetualFuture
from quant_common.data.instruments.perpetual_future.loaders import PerpetualFutureDataLoader
from quant_common.data.registry import InstrumentRegistry


class MarketDataService:
    """Loads configured instruments for one shared start-inclusive date range."""

    def __init__(
        self,
        instruments: Sequence[Instrument],
        start_date: date,
        end_date: date,
        *,
        config: DataConfig | None = None,
        registry: InstrumentRegistry | None = None,
    ) -> None:
        if start_date >= end_date:
            raise ValueError("start_date must be earlier than end_date (exclusive)")
        self.instruments = tuple(instruments)
        self.start_date = start_date
        self.end_date = end_date
        self.config = config or DataConfig.from_env()
        self.registry = registry or InstrumentRegistry()
        self.perpetual_future_loader = PerpetualFutureDataLoader(
            storage_path=self.config.storage_path,
        )

    def load(self) -> InstrumentRegistry:
        """Load all configured instruments, register datasets, and return registry."""
        for instrument in self.instruments:
            if isinstance(instrument, PerpetualFuture):
                self.load_perpetual_future(instrument)
            else:
                raise NotImplementedError(
                    f"No instrument loading method for {type(instrument).__name__}"
                )
        return self.registry

    def load_perpetual_future(self, instrument: PerpetualFuture) -> MarketDataset:
        """Load and register one perpetual future using loader-owned routing."""
        dataset = self.perpetual_future_loader.load(
            instrument,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        self.registry.register(instrument, dataset)
        return dataset

    def get(self, instrument: Instrument | str) -> MarketDataset:
        """Retrieve a loaded dataset by instrument config or stable key."""
        return self.registry.get(instrument)

    @property
    def storage_path(self) -> Path:
        return Path(self.config.storage_path)
