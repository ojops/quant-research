# Quantitative Research

A Python project for reproducible single-asset return analysis and cost-aware backtesting. This is a research baseline, **not** a validated profitable strategy or live trading system.

[![Eight-second preview of the synthetic backtest](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4)

*Preview: a backtest on synthetic prices. [Watch the full 38-second demonstration (MP4)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4) · [How the video is made](docs/DEMO.md).*

## Overview

This project provides an inspectable starting point for investigating trading rules: validate a price series, form a momentum signal, simulate a long-or-cash strategy with trading costs, and compare its results with buy-and-hold and cash. A checksum-pinned experiment can declare its hypothesis, data provenance, evaluation period and complete parameter/cost comparisons before running.

The bundled example uses **synthetic prices** to demonstrate the implementation, not to establish investment performance. Independent real-data evaluation and statistical validation are future development priorities.

## Features

- Validate dated adjusted-close prices from CSV
- Calculate returns, equity, volatility, Sharpe ratio and maximum drawdown
- Backtest a fixed momentum rule with long-or-cash positions
- Account for proportional trading costs, turnover and weight drift
- Compare momentum, buy-and-hold and cash over identical, explicitly bounded periods
- Reproduce JSON experiments with input, configuration and implementation checksums
- Report every declared lookback/cost variation without automatic selection
- Choose idealised signal-close or delayed next-close execution
- Export results, dated return paths, parameters and comparisons as JSON

The implementation covers **one asset** with idealised close-based execution. It does not download data, fit parameters or trade live.

## Requirements and Installation

Requires Python 3.10 and [uv](https://docs.astral.sh/uv/). These commands target Ubuntu or WSL. Core calculations use only the Python standard library.

```bash
git clone https://github.com/ojops/quant-research.git
cd quant-research
uv sync --locked
```

## Usage

The bundled prices are **synthetic** and are intended to test the implementation, not demonstrate investment performance.

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01 --lookback 5 --cost-bps 10
```

CSV input requires strictly increasing, unique `date` values (`YYYY-MM-DD`) and positive finite `adjusted_close` values. The CLI does not download, adjust or fill missing prices.

Reproduce the bundled **development** experiment (nine fixed settings, each compared with buy-and-hold and cash):

```bash
uv run quant-research --experiment examples/synthetic_experiment.json
```

Paths in the experiment are relative to its JSON file. A changed input checksum is rejected, and CLI parameter overrides cannot silently alter the declaration. The example uses an additional one-observation execution delay and remains synthetic.

For a single run with a fixed endpoint and delayed execution:

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01 --test-end 2024-03-22 --execution-lag 1
```

Output JSON includes strategy, cash and buy-and-hold paths, valuation and signal dates, performance metrics, settings and an input SHA-256 checksum. Experiment reports also retain the full configuration, source hashes and a flat comparison table. Run `uv run quant-research --help` for options.

## Research Method and Limitations

The signal compares the current price with its price `lookback` observations earlier. A signal calculated using the close at time `t` applies to the **following** return interval, not the interval that produced it.

The original CLI defaults remain idealised signal-close execution (`--execution-lag 0`). With lag 1, a signal observed at close `t` fills at close `t+1` and first earns the `t+1` to `t+2` return. Adjusted closing prices still approximate fills; this is not a validated execution model. All models start in cash, pay applicable proportional costs and use zero cash/risk-free return with no forced final liquidation.

Experiment roles distinguish development grids from a declared holdout with one fixed setting. The declaration cannot prove the data were untouched. A chronological evaluation period alone does not establish statistical significance. See [research and accounting notes](docs/RESEARCH.md).

## Development Roadmap

The priority is to progress from a reproducible synthetic backtest to defensible empirical research. Improving the experimental methodology takes precedence over adding visual effects.

### Planned

- **Use traceable real market data:** populate the implemented provenance manifest with independently checked sources, licences, adjustments and immutable snapshots; audit missing observations and selection bias.
- **Conduct a genuinely untouched evaluation:** preregister a substantive hypothesis and one fixed setting, retain development comparisons, then evaluate new data once. Configuration support is implemented; empirical validation is not.
- **Assess uncertainty:** add methods suited to dependent returns and multiple comparisons before interpreting sensitivity tables as evidence.
- **Validate execution and visuals:** test next-close assumptions against executable prices and order timing; generalise chart dates and labels when moving beyond the fixed synthetic film.

## Project Structure

```text
quant-research/
├── examples/
│   ├── synthetic_prices.csv       # Deterministic example price data
│   └── synthetic_experiment.json  # Declared development sensitivity grid
├── src/quant_research/
│   ├── data.py                    # CSV loading and validation
│   ├── analysis.py                # Returns and risk statistics
│   ├── backtest.py                # Signals and cost-aware backtesting
│   ├── evaluation.py              # Common horizons, timing and cash baseline
│   ├── experiment.py              # Configuration, provenance and comparisons
│   └── main.py                    # CLI and JSON reporting
├── scripts/                       # Portfolio video rendering
├── tests/                         # Research and demonstration tests
├── docs/                          # Research and demo documentation
│   └── media/                     # Preview GIF, MP4 and recorded data
├── pyproject.toml                 # Project metadata and dependencies
├── uv.lock                        # Locked dependencies
└── README.md
```

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Dependencies are managed with `uv`; when changing them, commit both `pyproject.toml` and `uv.lock`. GitHub Actions runs automated checks. See [coding conventions](docs/STYLE.md).

## License

[MIT licensed](LICENSE).
