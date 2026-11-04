# Research and accounting notes

This document explains the mathematics and assumptions behind the single asset backtest. Start with the [README](../README.md) for installation and command line usage.

## Returns and risk

Let `p_t` denote the adjusted closing price at observation `t`.

### Simple returns and wealth

The simple return for one interval is:

```text
r_t = p_t / p_(t-1) - 1
```

For wealth `V_t`, compound returns rather than summing them:

```text
V_t = V_(t-1) * (1 + r_t),   V_0 = 1
```

Including initial wealth in the equity curve ensures that a loss in the first interval contributes to drawdown.

### Drawdown

Drawdown is the loss relative to the highest wealth reached so far:

```text
drawdown_t = V_t / max(V_0, ..., V_t) - 1
```

Maximum drawdown is the minimum of this series and is reported as a **negative fraction** (or zero if there is no drawdown).

### Annualised statistics

For `n` observed return intervals and `K` intervals per year:

| Metric | Calculation |
| --- | --- |
| Annualised compound return | `(V_n / V_0)^(K/n) - 1` |
| Annualised volatility | `sample_stdev(r) * sqrt(K)` |
| Sharpe ratio (zero risk free rate) | `mean(r) / sample_stdev(r) * sqrt(K)` |

The Sharpe ratio is reported as JSON `null` when sample volatility is zero or fewer than two returns are available. Total return and drawdown remain meaningful with a single observed return.

These are **descriptive measures, not confidence intervals**. Annualising short or dependent return samples can be misleading. The default `K=252` assumes daily trading observations, the program does not infer missing sessions or regularise timestamps.

## Signal timing and look ahead bias

The momentum rule chooses a target long weight of 1 if the current adjusted close is above the close `lookback` observations earlier, otherwise it chooses 0 (cash).

A target `w_t` based on prices available **through close `t`** earns the return from `t` to `t+1`. It must never earn the price change ending at `t`, because that would use future information.

Tests check that adding later data does not change earlier signals and that a 100% price jump cannot be captured by the signal created by that jump.

**Execution caveat:** Applying the newly computed target at the same observed close assumes that close is tradable after the signal is known. This simplifies accounting, a realistic next session execution model requires a separate execution price series.

## Transaction costs and portfolio drift

The backtest charges proportional costs on the asset value actually traded, rather than simply on changes to target weights.

### Drift before rebalancing

Even if the desired portfolio weight is unchanged, the asset weight drifts after a return.

For previous target weight `w` and interval asset return `r`, the pretrade asset fraction is:

```text
x = w * (1 + r) / (1 + w * r)
```

Ignoring this drift would understate turnover when rebalancing fractional allocations.

### Costs applied to invested capital

Define:

- `c`: proportional cost rate (`cost-bps / 10000`)
- `x`: pretrade asset fraction of wealth
- `w`: target asset fraction of wealth **after costs**
- `f`: cost as a fraction of pretrade wealth

The accounting identity is:

```text
f = c * abs(w * (1 - f) - x)
```

Solving this identity for trade direction gives:

```text
Buy:  f = c * (w - x) / (1 + c * w)
Sell: f = c * (x - w) / (1 - c * w)
```

Actual turnover and the next net interval return are:

```text
turnover   = abs(w * (1 - f) - x)
net_return = (1 - f) * (1 + w * r) - 1
```

This accounts for fees reducing the capital available to invest. With flat prices, fully entering and then exiting produces final wealth `(1-c)/(1+c)`, rather than exactly `(1-c)^2`.

Costs represent constant proportional fees and slippage, **not** order book execution. The model does not force liquidation on the final observation, the last signal has no observed subsequent return and is ignored.

## Evaluation period and reproducibility

The `--test-start` argument selects a date present in the input and requires enough earlier observations for the lookback signal. The strategy and buy and hold evaluation start flat over the same horizon, including relevant initial entry costs. Warm up prices supply history only, they are not a fitted training set.

The CLI returns a SHA-256 checksum for the input and records parameters in JSON so a result can be matched to its dataset and configuration. The bundled example is synthetic rather than a market sample.

Tests cover causality, input rejection, drawdown, turnover after drift, fee accounting, zero cost buy and hold agreement with price ratios, and reproducible CLI output. Full return and position paths permit more scrutiny than a headline Sharpe ratio alone.

## Designing a defensible next experiment

1. **Define the question first.** Choose an asset or universe and a hypothesis before reviewing performance
2. **Document the data.** Record the source, licence, adjustment rules, retrieval date, checksum, trading calendar, missing observations, and selection or survivorship limitations.
3. **Separate development and evaluation.** Freeze the development period, validation procedure and final untouched holdout. The current CLI is not a model fitting framework
4. **Predeclare comparisons.** Include cash and buy and hold baselines and transaction cost sensitivity, and report all tried variants
5. **Quantify uncertainty.** Use methods that account for serial dependence (such as an appropriate block bootstrap), rather than treating a single backtest score as a reliable estimate

Portfolios, live execution and machine learning models are deliberately out of scope for this baseline. Standard library loops are sufficient for its small daily single asset workload, add scientific dependencies when a measurable research requirement justifies them.
