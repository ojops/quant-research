# Quantitative Research

A small Python 3.10 research foundation for validated single-asset prices,
financial returns, risk metrics and cost-aware backtests. It uses only the
standard library at runtime. This replaces an empty scaffold; it is not a mature
research platform or evidence of a profitable trading strategy.

```bash
uv sync --locked
uv run pytest
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01
uv run python -m quant_research examples/synthetic_prices.csv --test-start 2024-02-01 --lookback 5 --cost-bps 10
```

The CSV requires `date` (ISO YYYY-MM-DD) and `adjusted_close` (finite positive
number), strictly increasing dates and no duplicates. Data are never downloaded,
sorted, forward-filled or adjusted automatically. The caller is responsible for
correct split/dividend adjustment and consistent observation spacing.

## Research experiment

A fixed trailing-price momentum rule is long when price(t)>price(t-lookback),
and otherwise holds cash. Signals use information available through t and earn
only the following interval's return. The holdout starts at `--test-start`, which
must occur in the data and have enough prior warm-up history. Both the strategy
and buy-and-hold start flat and pay initial entry costs on this same horizon.
Prior observations supply signal history; no parameters are fitted automatically.

JSON output includes the input SHA-256, settings, evaluation dates, net returns,
positions, turnover, costs, total/annualised returns, sample volatility,
zero-risk-free Sharpe and maximum drawdown. The bundled 60-observation example
is synthetic: p_i=100*exp(0.0005*i+0.03*sin(i/3)), rounded to eight decimals, on
weekdays starting 2024-01-01. It is a reproducible functional fixture, not market
data or a strategy evaluation. No paid services or API credentials are required.

## Assumptions and limitations

- One asset, long-only weights in [0,1], zero-return cash, no leverage or shorts.
- Close-to-close accounting assumes execution at the observed signal close;
  this is an idealised fill assumption, not proof the close was achievable after
  signal calculation. A next-open execution model needs different input data.
- `cost-bps` is a constant proportional fee/slippage model, not an order book.
  It applies to actual asset value traded, including entry and weight drift.
  There is no forced final liquidation. The final signal has no observed future
  return and is ignored.
- Annualisation assumes the specified observation frequency (default 252/year).
  Missing sessions and irregular timestamps are not inferred. Inspect them first.
- Sharpe uses sample volatility, a zero risk-free rate, and square-root-of-time
  scaling. Autocorrelation and non-stationarity can invalidate its interpretation.
  Undefined Sharpe is JSON null, not infinity.
- A chronological holdout alone cannot prevent manual tuning on test results,
  survivorship bias in source selection or errors in adjusted data. Do not select
  parameters after inspecting this holdout and then call it out-of-sample evidence.

See [mathematical and accounting notes](docs/RESEARCH.md) and
[coding standard](docs/STYLE.md). Next: source and snapshot a real dataset, compare
fixed baselines across predeclared periods and assess statistical uncertainty.
MIT licensed; see [LICENSE](LICENSE).
