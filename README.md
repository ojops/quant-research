# Quantitative Research

A Python project for reproducible single-asset return analysis and cost-aware backtesting. This is a research baseline, **not** a validated profitable strategy or live trading system.

[![Eight-second preview of the synthetic backtest](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4)

*Preview: a backtest on synthetic prices. [Watch the full 38-second demonstration (MP4)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4) · [How the video is made](docs/DEMO.md).*

## Overview

Validate a price series, backtest a fixed momentum rule with trading costs, and compare it with buy-and-hold and cash. Experiment files record the hypothesis, data provenance, evaluation period, and parameter comparisons alongside input and source checksums.

The bundled prices are **synthetic**. Real-data evaluation and statistical validation remain future work.

## Features

- Validate dated adjusted-close prices from CSV
- Calculate returns, equity, volatility, Sharpe ratio, and maximum drawdown
- Backtest a fixed momentum rule with long-or-cash positions
- Account for proportional trading costs, turnover, and weight drift
- Compare momentum, buy-and-hold, and cash over identical periods
- Reproduce JSON experiments with input, configuration, and implementation checksums
- Report every declared lookback/cost variation without automatic selection
- Choose idealised signal-close or delayed next-close execution
- Export results, dated return paths, parameters, and comparisons as JSON

The implementation covers **one asset** with idealised close-based execution. It does not download data, fit parameters, or trade live.

## Requirements and Installation

Requires Python 3.10 and [uv](https://docs.astral.sh/uv/). These commands target Ubuntu or WSL. Core calculations use only the Python standard library.

```bash
git clone https://github.com/ojops/quant-research.git
cd quant-research
uv sync --locked
```

## Usage

Run a single backtest on the bundled synthetic prices:

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01 --lookback 5 --cost-bps 10
```

CSV input requires strictly increasing, unique `date` values (`YYYY-MM-DD`) and positive finite `adjusted_close` values. Prices are not adjusted or filled by the CLI.

Reproduce the bundled **development** experiment (nine fixed settings, each compared with buy-and-hold and cash):

```bash
uv run quant-research --experiment examples/synthetic_experiment.json
```

Paths are relative to the experiment JSON file. Input checksum mismatches and CLI parameter overrides are rejected. The example uses a one-observation execution delay. See the [experiment schema](docs/RESEARCH.md#declared-experiment-files) to create your own declaration.

For a single run with a fixed endpoint and delayed execution:

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01 --test-end 2024-03-22 --execution-lag 1
```

JSON output includes dated paths, metrics, settings, and the input checksum for all three models. Experiment reports add the configuration, source hashes, and comparison table. Run `uv run quant-research --help` for all options.

## Research Method and Limitations

Momentum targets full investment when the current price exceeds the price `lookback` observations earlier, and cash otherwise.

The default `--execution-lag 0` assumes a fill at the signal close and earns the following interval. Lag 1 fills at the next observed close and earns the interval after that. Both use idealised adjusted-close fills. Models start in cash, pay applicable entry and rebalancing costs, and have no forced final liquidation. Cash and the risk-free rate are zero.

Experiment roles distinguish development grids from a declared holdout with one fixed setting. The declaration cannot prove the data were untouched. A chronological evaluation period alone does not establish statistical significance. See [research and accounting notes](docs/RESEARCH.md).

## Development Roadmap

The priority is to progress from a reproducible synthetic backtest to defensible empirical research. Improving the experimental methodology takes precedence over adding visual effects.

### Planned

- **Use traceable real market data:** verify sources, licences, adjustments, and immutable snapshots. Audit missing observations, and selection bias.
- **Conduct a genuinely untouched evaluation:** preregister a hypothesis and one fixed setting, retain development comparisons, and evaluate new data once. Configuration support exists, but empirical validation remains outstanding.
- **Assess uncertainty:** add methods suited to dependent returns and multiple comparisons before interpreting sensitivity tables as evidence.
- **Validate execution and visuals:** test next-close assumptions against executable prices and order timing. Generalise chart dates and labels beyond the fixed synthetic film.

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
│   ├── evaluation.py              # Common horizons, timing, and cash baseline
│   ├── experiment.py              # Configuration, provenance, and comparisons
│   └── main.py                    # CLI and JSON reporting
├── scripts/                       # Portfolio video rendering
├── tests/                         # Research and demonstration tests
├── docs/                          # Research and demo documentation
│   └── media/                     # Preview GIF, MP4, and recorded data
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

When changing dependencies, commit both `pyproject.toml` and `uv.lock`. GitHub Actions runs automated checks. See [coding conventions](docs/STYLE.md).

## License

[MIT licensed](LICENSE).
