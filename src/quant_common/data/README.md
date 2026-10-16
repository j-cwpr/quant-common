# Market data

`MarketDataService` loads configured instruments for one shared date range. The
range is start-inclusive and end-exclusive. The service dispatches supported
instruments through explicit instrument-specific methods; perpetual futures use
`load_perpetual_future(...)` and `PerpetualFutureDataLoader`.

## Consumer usage

Consumers specify instruments and dates. Provider setup and routing are owned by
the loader layer.

```python
from datetime import date

from quant_common.data import MarketDataService
from quant_common.data.instruments import PerpetualFuture

btc = PerpetualFuture(
    exchange="binance",
    symbol="BTCUSDT",
    data_types=("trades", "quotes"),
)
market_data = MarketDataService(
    instruments=[btc],
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 3),  # exclusive
)
registry = market_data.load()
dataset = registry.get(btc)
```

## Instrument keys and datasets

Instrument identity is a stable key independent of requested dates and data
types. Exchange values are lowercased and symbols uppercased. For example,
`PerpetualFuture(exchange="Binance", symbol="btcusdt").key` is
`perpetual_future:binance:BTCUSDT`.

The registry stores a `MarketDataset` under that key. Inspect registered keys
with `registry.keys()`, and retrieve data with `registry.get(instrument)` or
`registry.get(instrument.key)`. `MarketDataset.files_by_data_type` maps each
requested data type to its cached daily files, and its date fields describe the
requested coverage.

## Loader-owned provider routing

Each instrument loader checks local cache files first. On a cache miss, the
perpetual futures loader resolves a provider internally. Tardis is the initial
default. To override routing by data type, set
`QUANT_PERPETUAL_FUTURE_DEFAULT_PROVIDER` or provide a JSON map in
`QUANT_PERPETUAL_FUTURE_PROVIDER_OVERRIDES`, for example:

```text
QUANT_PERPETUAL_FUTURE_PROVIDER_OVERRIDES={"trades":"tardis","quotes":"other_source"}
```

Provider implementations are registered in the loader layer with
`register_provider(name, factory)`. The loader uses the configured override for
a data type when present, otherwise its default provider, and verifies that the
selected provider supports the requested instrument and data type. Provider
credentials are read by the provider implementation; Tardis reads
`TARDIS_API_KEY` from the environment. Set `QUANT_MARKET_DATA_PATH` to change
the cache root; it defaults to `data/market`.

Tardis symbols and data types must match the exchange's dataset metadata. Tardis
provides daily gzip-compressed CSV datasets; see its
[dataset API documentation](https://docs.tardis.dev/downloadable-csv-files/api).
