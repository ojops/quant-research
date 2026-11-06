# Quantitative Research

A Python 3.10 project for reproducible single-asset return analysis and cost-aware backtesting. A research baseline, **not** a validated profitable strategy or live trading system.

[![Eight-second looping preview of synthetic prices and positions](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4)

*Eight-second preview using synthetic prices. [Watch the full 38-second backtest demonstration (MP4)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4) · [Reproduce the demonstration](docs/DEMO.md).*

## Features

- Validated, dated adjusted-close prices from CSV
- Returns, compounded equity, volatility, Sharpe ratio and maximum drawdown
- Fixed lookback-momentum signals and long-or-cash backtesting
- Proportional trading costs, turnover and buy-and-hold comparison
- Chronological evaluation with JSON results, input checksums and automated tests

The example uses **one asset**, idealised close-based fills and a fixed rule; no parameter fitting or real-market performance is claimed.

## Requirements and installation

Python 3.10 and [uv](https://docs.astral.sh/uv/); commands below target Ubuntu/WSL. Core calculations use the standard library.

```bash
git clone https://github.com/ojops/quant-research.git
cd quant-research
uv sync --locked
```

## Usage

Run the included deterministic **synthetic** price example:

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01 --lookback 5 --cost-bps 10
```

Input CSV files require strictly increasing, unique `date` values (`YYYY-MM-DD`) and finite positive `adjusted_close` prices. Data is not downloaded or adjusted automatically.

Output is JSON containing the strategy and buy-and-hold paths, metrics, settings and source-file SHA-256. See `uv run quant-research --help` for options.

## Methodology and limitations

At close `t`, the momentum rule compares the current price with the price `lookback` observations earlier. The resulting position applies **only to the next return interval**; it does not earn the price move that produced the signal.

The model includes proportional trading costs and weight drift, but assumes idealised close fills, zero cash and risk-free returns and no forced final liquidation. A short chronological holdout does not remove selection bias or establish statistical significance. See [research notes](docs/RESEARCH.md) for the accounting and limitations.

## Project structure

- `src/quant_research/data.py` — input validation
- `analysis.py` and `backtest.py` — performance metrics, signals and trading simulation
- `main.py` — CLI and JSON reporting
- `examples/`, `tests/` and `docs/` — synthetic data, checks and methodology

## Roadmap

Add provenance-controlled real data, predeclared experiments, stronger statistical evaluation and more realistic execution assumptions.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

GitHub Actions runs automated checks. See [coding conventions](docs/STYLE.md). Licensed under [MIT](LICENSE).
