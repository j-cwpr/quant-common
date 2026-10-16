"""Perpetual futures instrument model."""

from dataclasses import dataclass, field
from typing import ClassVar

from quant_common.data.instruments.base import Instrument


@dataclass(frozen=True, slots=True)
class PerpetualFuture(Instrument):
    """A futures contract without expiry."""

    contract_size: float | None = None
    settlement_asset: str | None = None
    data_types: tuple[str, ...] = field(default=("trades",))
    instrument_type: ClassVar[str] = "perpetual_future"
