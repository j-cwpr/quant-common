"""Perpetual futures loader and its loader-owned provider configuration."""

from quant_common.data.instruments.perpetual_future.loaders.loader import (
    PerpetualFutureDataLoader,
    PerpetualFutureLoaderConfig,
    register_provider,
)

__all__ = [
    "PerpetualFutureDataLoader",
    "PerpetualFutureLoaderConfig",
    "register_provider",
]
