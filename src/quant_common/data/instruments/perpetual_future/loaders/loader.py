"""Perpetual futures data loading and provider routing."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
import json
import os
from pathlib import Path

from quant_common.data.cache import DatasetCache
from quant_common.data.dataset import MarketDataset
from quant_common.data.instruments.perpetual_future.instrument import PerpetualFuture
from quant_common.data.provider import MarketDataProvider
from quant_common.data.storage import LocalStorage
from quant_common.data.instruments.perpetual_future.sources.tardis import TardisProvider


ProviderFactory = Callable[[], MarketDataProvider]
_PROVIDER_FACTORIES: dict[str, ProviderFactory] = {}


def register_provider(name: str, factory: ProviderFactory) -> None:
    """Register a provider implementation with the perpetual futures loader layer."""
    _PROVIDER_FACTORIES[name] = factory


@dataclass(frozen=True, slots=True)
class PerpetualFutureLoaderConfig:
    """Loader-owned source defaults and optional per-data-type provider overrides."""

    default_provider: str = "tardis"
    provider_overrides: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "PerpetualFutureLoaderConfig":
        raw_overrides = os.getenv("QUANT_PERPETUAL_FUTURE_PROVIDER_OVERRIDES", "{}")
        overrides = json.loads(raw_overrides)
        if not isinstance(overrides, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in overrides.items()
        ):
            raise ValueError("QUANT_PERPETUAL_FUTURE_PROVIDER_OVERRIDES must be a JSON object of strings")
        return cls(
            default_provider=os.getenv("QUANT_PERPETUAL_FUTURE_DEFAULT_PROVIDER", "tardis"),
            provider_overrides=overrides,
        )


# Built-in sources are registered by the loader package. Additional source
# integrations can register factories here without changing MarketDataService.
register_provider("tardis", TardisProvider)


class PerpetualFutureDataLoader:
    """Loads cached futures data and routes cache misses to configured sources."""

    def __init__(
        self,
        storage_path: str | Path = "data/market",
        config: PerpetualFutureLoaderConfig | None = None,
        providers: dict[str, MarketDataProvider] | None = None,
    ) -> None:
        self.config = config or PerpetualFutureLoaderConfig.from_env()
        self.cache = DatasetCache(storage_path)
        self.providers = dict(providers or {})

    def load(self, instrument: PerpetualFuture, start_date: date, end_date: date) -> MarketDataset:
        if start_date >= end_date:
            raise ValueError("start_date must be earlier than end_date (exclusive)")
        files_by_data_type: dict[str, tuple[Path, ...]] = {}
        for data_type in instrument.data_types:
            data_files: list[Path] = []
            day = start_date
            while day < end_date:
                path = self.cache.path_for(instrument.key, data_type, day)
                if not path.exists():
                    provider = self._provider_for(instrument, data_type)
                    LocalStorage.prepare(path)
                    provider.download_dataset(
                        exchange=instrument.exchange,
                        data_type=data_type,
                        symbol=instrument.symbol,
                        day=day,
                        destination=path,
                    )
                    if not path.exists():
                        raise FileNotFoundError(
                            f"Provider {provider.name!r} did not create {path}"
                        )
                data_files.append(path)
                day += timedelta(days=1)
            files_by_data_type[data_type] = tuple(data_files)
        return MarketDataset(
            instrument_key=instrument.key,
            start_date=start_date,
            end_date=end_date,
            files_by_data_type=files_by_data_type,
        )

    def _provider_for(self, instrument: PerpetualFuture, data_type: str) -> MarketDataProvider:
        provider_name = self.config.provider_overrides.get(
            data_type, self.config.default_provider
        )
        provider = self.providers.get(provider_name)
        if provider is None:
            try:
                provider = _PROVIDER_FACTORIES[provider_name]()
            except KeyError as error:
                raise LookupError(f"Unknown market data provider {provider_name!r}") from error
            self.providers[provider_name] = provider
        if not provider.supports(instrument, data_type):
            raise LookupError(
                f"Provider {provider_name!r} does not support "
                f"{instrument.key} data type {data_type!r}"
            )
        return provider
