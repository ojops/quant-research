# Quantitative Research

Reproducible single-asset return analysis and cost-aware backtesting in Python 3.10. This is a research baseline, **not** a validated profitable strategy or live trading system.

[![Eight-second preview of the synthetic backtest](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4)

*Preview: a backtest on synthetic prices. [Watch the full 38-second demonstration (MP4)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4) · [How the video is made](docs/DEMO.md).*

## Features

- Validate dated adjusted-close prices from CSV
- Calculate returns, equity, volatility, Sharpe ratio and maximum drawdown
- Backtest a fixed momentum rule with long-or-cash positions
- Account for proportional trading costs, turnover and weight drift
- Compare with buy-and-hold over the same chronological evaluation period
- Export results, return paths, parameters and data checksums as JSON

The implementation covers **one asset** with idealised close-based execution. It does not download data, fit parameters or trade live.

## Install

Requires Python 3.10 and [uv](https://docs.astral.sh/uv/). These commands target Ubuntu or WSL. Core calculations use only the Python standard library.

```bash
git clone https://github.com/ojops/quant-research.git
cd quant-research
uv sync --locked
```

## Run

The bundled prices are **synthetic** and are intended to test the implementation, not demonstrate investment performance.

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01 --lookback 5 --cost-bps 10
```

CSV input requires strictly increasing, unique `date` values (`YYYY-MM-DD`) and positive finite `adjusted_close` values. The CLI does not download, adjust or fill missing prices.

Output JSON includes strategy and benchmark paths, performance metrics, settings and an input SHA-256 checksum. Run `uv run quant-research --help` for options.

## Method and limitations

The signal compares the current price with its price `lookback` observations earlier. A signal calculated using the close at time `t` applies to the **following** return interval, not the interval that produced it.

The model charges proportional trading costs but assumes execution at the observed signal close, a zero-return cash position, a zero risk-free rate for Sharpe, and no forced final liquidation. A chronological evaluation period alone does not establish statistical significance. See [research and accounting notes](docs/RESEARCH.md).

## Next steps

Use provenance-controlled market data, predeclare experiments, quantify statistical uncertainty and introduce more realistic execution assumptions.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

GitHub Actions runs automated checks. See [coding conventions](docs/STYLE.md). [MIT licensed](LICENSE).
