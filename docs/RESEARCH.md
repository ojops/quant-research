# Research methods and accounting

This document defines the calculations and assumptions of the single-asset backtest. For installation and CLI usage, see the [README](../README.md).

## Returns and risk metrics

Let `p_t` be the adjusted close at observation `t`. The simple return is:

```text
r_t = p_t / p_(t-1) - 1
```

Compound wealth from `V_0 = 1`:

```text
V_t = V_(t-1) × (1 + r_t)
```

Including the initial wealth ensures that a first-interval loss contributes to drawdown. For a running peak, drawdown is:

```text
D_t = V_t / max(V_0, ..., V_t) - 1
```

Maximum drawdown is the minimum `D_t`, reported as a **non-positive fraction**.

For `n` observed intervals and `K` intervals per year:

| Metric | Formula |
| --- | --- |
| Annualised compound return | `(V_n / V_0)^(K/n) - 1` |
| Annualised volatility | `sample_stdev(r) × sqrt(K)` |
| Sharpe (zero risk-free rate) | `mean(r) / sample_stdev(r) × sqrt(K)` |

Sharpe is `null` when there are fewer than two returns or sample volatility is zero. Annualised volatility is also `null` with fewer than two observations. The default `K=252` assumes trading-day intervals. The program neither infers the calendar frequency nor fills missing sessions. These are **descriptive metrics**, not uncertainty estimates.

Calculations use binary floating point. Before reporting an asset or post-cost
return, the model checks that converting its positive growth factor to `r` and
back to `1 + r` preserves that factor within `1e-10` relative error (zero absolute
tolerance). Extreme losses that fail this check are rejected: otherwise a price
round trip such as `1 → 1e-16 → 1` can manufacture a gain through cancellation.
This is a per-interval representation check, not a bound on cumulative error.
Positive equity that underflows to zero is also rejected. An explicitly supplied
return of -1 still represents a genuine total loss in the statistics API.

## Signal timing

The fixed momentum rule targets weight 1 (fully invested) when the current adjusted close exceeds the price `lookback` observations earlier. Otherwise it targets weight 0 (cash).

A signal uses only prices available at its observation close. Tests check that later observations cannot change earlier signals.

| Execution lag | Signal observed | Assumed fill | First return earned |
| --- | --- | --- | --- |
| 0 (CLI default) | Close `t` | Close `t` | `t` to `t+1` |
| 1 | Close `t` | Close `t+1` | `t+1` to `t+2` |

Lag 0 assumes an idealised fill at the close used to form the signal. Lag 1 avoids that requirement. The delay counts **observations**, not calendar days. The first valuation requires `lookback + execution_lag` prior observations.

**Remaining limitation:** next-close execution still assumes an achievable adjusted-close fill, constant proportional costs, and no order constraints. It does not model next-open execution, intraday prices, corporate-action cash flows, or liquidity. The earlier signal can be submitted before the execution close, but historical adjusted prices are not themselves an executable quote. Neither mode establishes real trading feasibility.

## Transaction costs and portfolio drift

Costs are proportional to value traded, including rebalancing caused by portfolio weight drift. In the formulas below, `r_cash` is the interval’s cash return. It defaults to zero; the monthly follow-up supplies historical cash returns.

For a previous target weight `w` and asset return `r`, the asset's weight before the next rebalance is:

```text
x = w × (1 + r) / (1 + w × r + (1 - w) × r_cash)
```

Define `c = cost_bps / 10000`, `x` as the pretrade weight, `w` as the **post-cost** target weight, and `f` as fees divided by pretrade wealth. The accounting identity is:

```text
f = c × abs(w × (1 - f) - x)
```

For each trade direction, it simplifies to:

```text
Buy:  f = c × (w - x) / (1 + c × w)
Sell: f = c × (x - w) / (1 - c × w)
```

The recorded turnover and next net return are:

```text
turnover   = abs(w × (1 - f) - x)
net_return = (1 - f) × (1 + w × r + (1 - w) × r_cash) - 1
```

Fees reduce investable capital. With flat prices, entering fully and then exiting leaves wealth `(1 - c) / (1 + c)`, rather than exactly `(1 - c)^2`.

The rate approximates constant proportional fees and slippage. It does not model an order book or market impact. No final liquidation is forced. The last signal has no observed subsequent return and is not executed.

## Evaluation and reproducibility

`--test-start` and optional `--test-end` select inclusive valuation dates present in the CSV. At least three prices (two intervals) are required. Earlier prices provide signal warm-up, not fitting or a reported training backtest. The last valuation has no subsequent executed trade. Every variant uses exactly the same dates. Insufficient history for **any** declared lookback fails the entire experiment instead of shortening its horizon.

Strategy, buy-and-hold, and zero-return cash start flat over that period. The predeclared buy-and-hold baseline enters immediately at the first valuation close in both execution modes. It needs no momentum signal or delay. Both invested models pay applicable initial entry costs. Cash has zero turnover, costs, and return. Its Sharpe is undefined (`null`).

CLI JSON records the input SHA-256, settings, positions, returns, turnover, costs, and metrics. The bytes hashed are the same snapshot parsed. `valuation_dates[i:i+2]` brackets return `i`. `signal_dates[i]` dates the strategy information used for that interval. The bundled price series is deterministic and synthetic.

A chronological evaluation period is **not** automatically an untouched holdout: inspecting results and then changing strategy settings creates selection bias. The baseline does not estimate significance or correct for multiple comparisons.

## Developing a defensible experiment

1. **Specify the hypothesis** and instruments before looking at results.
2. **Record data provenance:** source, licence, adjustments, retrieval date, checksum, missing observations, and selection limitations.
3. **Separate development and final evaluation:** set periods and tuning rules in advance, leaving a genuinely untouched holdout.
4. **Predeclare comparisons:** include cash, buy-and-hold, trading costs, and every tested variant.
5. **Report uncertainty:** choose methods suited to dependent time-series observations, rather than trusting a single Sharpe ratio.

Multiple assets, realistic execution, and model fitting remain outside this small baseline.

## Declared experiment files

Run `uv run quant-research --experiment examples/synthetic_experiment.json`. The [complete example](../examples/synthetic_experiment.json) is schema version 1, with these required fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `name`, `hypothesis` | Nonempty human-readable declaration of the research question |
| `data.path`, `data.sha256` | Local snapshot, relative to the configuration file, and its exact SHA-256 |
| `data.provenance` | `kind` (`synthetic` or `market`), `source`, `licence`, `adjustments`, `retrieved_at`, and `limitations`. All descriptive text |
| `evaluation.start`, `evaluation.end` | Inclusive ISO valuation dates. Endpoints must be observed |
| `evaluation.role` | `development` or `declared_holdout` |
| `parameters.lookbacks`, `parameters.cost_bps` | Nonempty, duplicate-free lists. Every Cartesian pair is reported |
| `parameters.periods_per_year` | Positive integer observation frequency for annualisation |
| `parameters.execution_lag` | 0 or 1. Explicit for reproducibility |

Unknown keys, duplicate JSON keys, nonfinite numbers, invalid parameters, and checksum mismatches are errors. Provenance is recorded, **not independently certified**. For generated inputs, say why retrieval is inapplicable. For market inputs, supply an actual retrieval date and verified licensing/adjustment details. No data are downloaded.

A `declared_holdout` permits only one lookback and one cost setting. This is a guard against accidental sensitivity exploration, not a security barrier or proof of preregistration. Commit the declaration before inspecting evaluation results and retain all prior investigations. If results influence changes, treat that period as development and obtain new evaluation data.

Reports retain the raw-configuration and input SHA-256 checksums, parsed configuration, installed Python source hashes, Python version, complete model return paths, and a flat `comparison` array. Run numbers index `runs`. Rows preserve declaration order and are **not ranked by performance**. Each grid cell repeats buy-and-hold and cash for a self-contained comparison.

No timestamp is injected. Unchanged inputs, source, and interpreter produce deterministic JSON. Archive the Git commit, report, configuration, CSV, and `uv.lock` together. Hashes identify files but cannot recover missing snapshots.

The nine-setting example uses 36 intervals from 2024-02-01 through 2024-03-22 with lag 1. Existing single-run commands and the portfolio film retain lag 0 and their original numerical results. Sensitivity is descriptive. It does not estimate uncertainty, correct multiple testing, or identify a profitable strategy.

## Efficient uncertainty calculations

The paired bootstrap reuses circular block totals instead of building a full
return array for every resample. It retains the same seeded block draws, including
a shortened final block. Tests compare its percentile intervals with direct
resampling. Floating-point summation can differ in the last few digits. This
changes computation cost, not the declared research protocol. Committed historical
reports retain their original implementation hashes; reruns record current hashes.
