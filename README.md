# Quantitative Research

A Python project for reproducible single-asset return analysis and cost-aware backtesting. This is a research baseline, **not** a validated profitable strategy or live trading system.

[![Eight-second preview of the synthetic backtest](docs/media/preview.gif)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4)

*Preview: a backtest on synthetic prices. [Watch the full 38-second demonstration (MP4)](https://raw.githubusercontent.com/ojops/quant-research/04655a037b8421d7d7e9f633b05b149262a29da3/docs/media/demo.mp4) · [How the video is made](docs/DEMO.md).*

## Overview

Validate a price series, backtest a fixed momentum rule with trading costs, and compare it with buy-and-hold and cash. Experiment files record the hypothesis, data provenance, evaluation period, and parameter comparisons alongside input and source checksums.

The bundled synthetic example tests the implementation. A separate [completed historical AAPL pilot](research/results/apple-momentum.md) investigates archived market prices with a fixed protocol, chronological evaluation, cost/lookback sensitivity and paired block-bootstrap uncertainty. This is a limited retrospective study, **not** a genuinely unseen test or evidence of general profitability.

## Research result and reproduction

On the fixed 2016 evaluation, the 20-observation momentum rule at 10 bps turnover cost returned **8.61%**, versus **12.27%** for buy-and-hold. Maximum drawdown was **−11.69%** versus **−18.92%**. The lower drawdown came with lower return; all three bootstrap intervals for the mean return difference include zero. Costs and lookback materially affect results. No setting is selected or promoted as a profitable strategy.

After installation, reproduce the complete report with:

```bash
uv run python scripts/fetch_study_data.py
uv run python -m quant_research.study
```

The first command needs network access to `raw.githubusercontent.com`; it verifies the immutable source checksum before writing local data. The second is offline and writes `research/results/apple-momentum.json` and `.md`. Raw/normalised third-party prices remain ignored by Git. All calculation settings and bootstrap seeds are explicit; Python and implementation metadata are retained.

Read [the fixed protocol](docs/STUDY_PLAN.md), [findings and limitations](research/results/apple-momentum.md), and [machine-readable results](research/results/apple-momentum.json). JSON includes source hashes, the data-quality audit, every sensitivity setting, fixed-rule paths and uncertainty calculations. This is one retrospectively chosen stock from 2015–2017; 2017 is excluded from every reported evaluation. It does not establish broad or live trading performance.

### What to inspect

- `backtest.py` and `evaluation.py`: portfolio accounting and causal signal/execution timing.
- `experiment.py`: declared synthetic/custom experiments and provenance checks.
- `study.py`: fixed historical design, data audit, paired block bootstrap and report generation.
- `tests/test_study.py`: paired-return checks, checksum rejection and future-data invariance; existing tests cover the underlying accounting.

The historical runner builds on the existing backtester. It performs no fitting, automatic parameter selection or machine learning.

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

The implementation covers **one asset** with idealised close-based execution. The core CLI does not download data, fit parameters, or trade live; the separate study fetch script downloads one fixed snapshot.

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

The historical pilot is complete; the priority is now broader, independently validated empirical research. Improving the experimental methodology takes precedence over adding visual effects.

### Planned

- **Broaden the historical pilot:** obtain longer, independently checked multi-asset data with clear data rights and corporate-action treatment; audit missing sessions against exchange calendars.
- **Conduct a genuinely untouched evaluation:** preregister a hypothesis and one fixed setting, retain development comparisons, and evaluate new data once. The completed historical pilot does not satisfy this prospective goal.
- **Extend uncertainty assessment:** the pilot includes paired circular-block intervals; investigate structural breaks and multiple-comparison controls before making inferential claims.
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
│   ├── study.py                   # Historical pilot and uncertainty report
│   └── main.py                    # CLI and JSON reporting
├── research/results/              # Completed historical pilot and JSON evidence
├── scripts/                       # Data fetch and portfolio video rendering
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

Code is [MIT licensed](LICENSE). Third-party financial data is not relicensed by this repository; the study downloader keeps it local.
