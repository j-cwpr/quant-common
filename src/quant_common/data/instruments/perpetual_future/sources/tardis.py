"""Tardis historical CSV dataset provider."""

from datetime import date, timedelta
import os
from pathlib import Path
from typing import Any

from tardis_dev import download_datasets, get_exchange_details

from quant_common.data.instruments.base import Instrument
from quant_common.data.instruments.perpetual_future.instrument import PerpetualFuture
from quant_common.data.provider import MarketDataProvider


class TardisProvider(MarketDataProvider):
    """Historical dataset provider backed by Tardis."""

    name = "tardis"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("TARDIS_API_KEY")

    def supports(self, instrument: Instrument, data_type: str) -> bool:
        return isinstance(instrument, PerpetualFuture) and data_type in {
            "trades",
            "quotes",
            "incremental_book_L2",
            "book_snapshot_5",
            "book_snapshot_25",
            "derivative_ticker",
            "liquidations",
        }

    def list_instruments(self, exchange: str) -> list[dict[str, Any]]:
        details = get_exchange_details(exchange)
        return list(details.get("datasets", {}).get("symbols", []))

    def download_dataset(
        self,
        *,
        exchange: str,
        data_type: str,
        symbol: str,
        day: date,
        destination: Path,
    ) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)

        def destination_filename(*args: Any, **kwargs: Any) -> str:
            return destination.name

        download_datasets(
            exchange=exchange,
            data_types=[data_type],
            from_date=day.isoformat(),
            to_date=(day + timedelta(days=1)).isoformat(),
            symbols=[symbol],
            api_key=self.api_key,
            download_dir=str(destination.parent),
            get_filename=destination_filename,
        )
        if not destination.exists():
            raise FileNotFoundError(f"Tardis did not create expected dataset: {destination}")
        return destination
