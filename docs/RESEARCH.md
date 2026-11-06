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

Sharpe is `null` when there are fewer than two returns or sample volatility is zero. Annualised volatility is also `null` with fewer than two observations. The default `K=252` assumes trading-day intervals; the program neither infers the calendar frequency nor fills missing sessions. These are **descriptive metrics**, not uncertainty estimates.

## Signal timing

The fixed momentum rule targets weight 1 (fully invested) when the current adjusted close exceeds the price `lookback` observations earlier. Otherwise it targets weight 0 (cash).

A signal determined at close `t` applies to the return **from `t` to `t+1`**, not the return ending at `t`. Tests check that later observations cannot change earlier signals.

**Execution limitation:** The model assumes a position based on the close can be filled at that same close. Real trading would need an explicit order-timing convention and subsequent execution prices. Using a lagged return prevents direct signal/return look-ahead in the model, but does not make this fill assumption realistic.

## Transaction costs and portfolio drift

Costs are proportional to value traded, including rebalancing caused by portfolio weight drift.

For a previous target weight `w` and asset return `r`, the asset's weight before the next rebalance is:

```text
x = w × (1 + r) / (1 + w × r)
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
net_return = (1 - f) × (1 + w × r) - 1
```

Fees reduce investable capital. With flat prices, entering fully and then exiting leaves wealth `(1 - c) / (1 + c)`, rather than exactly `(1 - c)^2`.

The rate approximates constant proportional fees and slippage; it does not model an order book or market impact. No final liquidation is forced. The last signal has no observed subsequent return and is not executed.

## Evaluation and reproducibility

`--test-start` selects an observation with sufficient preceding history. Earlier prices are used only to calculate signals, not to fit parameters. Strategy and buy-and-hold start flat over the same evaluation period and pay applicable entry costs.

CLI JSON records the input SHA-256, settings, positions, returns, turnover, costs and metrics. The bundled price series is deterministic and synthetic.

A chronological evaluation period is **not** automatically an untouched holdout: inspecting results and then changing strategy settings creates selection bias. The baseline does not estimate significance or correct for multiple comparisons.

## Developing a defensible experiment

1. **Specify the hypothesis** and instruments before looking at results.
2. **Record data provenance:** source, licence, adjustments, retrieval date, checksum, missing observations and selection limitations.
3. **Separate development and final evaluation:** set periods and tuning rules in advance, leaving a genuinely untouched holdout.
4. **Predeclare comparisons:** include cash, buy-and-hold, trading costs and every tested variant.
5. **Report uncertainty:** choose methods suited to dependent time-series observations, rather than trusting a single Sharpe ratio.

Multiple assets, realistic execution and model fitting remain outside this small baseline.
