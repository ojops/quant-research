# Long-horizon industry momentum follow-up

## Design and data

Fixed 12-month lookback, one-month execution delay and 10bps cost. No parameter selection. All other settings are descriptive sensitivity, not independent holdouts. Equal initial capital in 12 independent sleeves; no cross-sleeve rebalancing.

[Protocol](../../docs/FOLLOWUP_PLAN.md) recorded before return inspection. Archive: 819 contiguous months, January 1949–March 2017, 12 industries. Development is 1980–1999; evaluation is 2000–2016 (204 months). Other observations provide warm-up or remain excluded. Monthly resolution is different from the daily AAPL pilot; this is not an exact replication.

Cash earns contemporaneous RF. Signal through month t is traded at the end of t+1 and first earns t+2. All models start flat; buy-and-hold pays entry costs. No terminal liquidation. Sharpe uses monthly returns minus RF; volatility is sample volatility of actual returns, annualised by sqrt(12).

## Fixed aggregate result

| Model | Total return | Annualised return | Annualised volatility | Excess-cash Sharpe | Max drawdown |
|---|---:|---:|---:|---:|---:|
| strategy | 175.27% | 6.14% | 9.60% | 0.498 | -20.72% |
| buy_and_hold | 208.87% | 6.86% | 13.61% | 0.437 | -47.09% |
| cash | 31.75% | 1.64% | 0.57% | undefined | 0.00% |

Fixed-rule cumulative return minus buy-and-hold: **-33.60 percentage points**. Maximum drawdown: -20.72% versus -47.09%. This is a historical comparison, not a profitability or significance claim.

## Every industry at the fixed setting

| Industry | Strategy return | Buy-and-hold return | Strategy drawdown | Buy-and-hold drawdown |
|---|---:|---:|---:|---:|
| NoDur | 361.95% | 429.72% | -17.76% | -33.90% |
| Durbl | 65.91% | 90.28% | -38.79% | -72.97% |
| Manuf | 180.40% | 305.47% | -39.39% | -59.36% |
| Enrgy | 282.44% | 302.62% | -47.19% | -49.83% |
| Chems | 103.47% | 234.43% | -27.22% | -43.75% |
| BusEq | 75.63% | 25.03% | -46.70% | -79.60% |
| Telcm | 232.49% | 27.74% | -19.02% | -71.89% |
| Utils | 262.40% | 371.99% | -31.11% | -38.49% |
| Shops | 123.97% | 227.04% | -36.40% | -38.41% |
| Hlth | 145.43% | 235.86% | -28.13% | -35.36% |
| Money | 86.90% | 146.32% | -27.50% | -71.83% |
| Other | 182.30% | 109.94% | -20.74% | -61.37% |

## Development grid

| Period | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |
|---|---:|---:|---:|---:|---:|
| 1980-01–1999-12 | 3 | 0 | 758.01% | 2323.69% | -29.53% |
| 1980-01–1999-12 | 3 | 10 | 714.31% | 2321.27% | -29.68% |
| 1980-01–1999-12 | 3 | 50 | 560.83% | 2311.63% | -30.29% |
| 1980-01–1999-12 | 6 | 0 | 1057.75% | 2323.69% | -28.62% |
| 1980-01–1999-12 | 6 | 10 | 1019.71% | 2321.27% | -28.63% |
| 1980-01–1999-12 | 6 | 50 | 879.90% | 2311.63% | -28.66% |
| 1980-01–1999-12 | 12 | 0 | 1499.48% | 2323.69% | -28.39% |
| 1980-01–1999-12 | 12 | 10 | 1466.21% | 2321.27% | -28.39% |
| 1980-01–1999-12 | 12 | 50 | 1340.10% | 2311.63% | -28.38% |

## Evaluation sensitivity (not fresh holdouts)

| Period | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |
|---|---:|---:|---:|---:|---:|
| 2000-01–2016-12 | 3 | 0 | 183.52% | 209.18% | -15.74% |
| 2000-01–2016-12 | 3 | 10 | 170.63% | 208.87% | -16.33% |
| 2000-01–2016-12 | 3 | 50 | 124.71% | 207.64% | -18.64% |
| 2000-01–2016-12 | 6 | 0 | 217.20% | 209.18% | -14.64% |
| 2000-01–2016-12 | 6 | 10 | 208.76% | 208.87% | -14.81% |
| 2000-01–2016-12 | 6 | 50 | 177.25% | 207.64% | -15.97% |
| 2000-01–2016-12 | 12 | 0 | 179.83% | 209.18% | -20.50% |
| 2000-01–2016-12 | 12 | 10 | 175.27% | 208.87% | -20.72% |
| 2000-01–2016-12 | 12 | 50 | 157.84% | 207.64% | -21.61% |

## Fixed-rule subperiods, each restarting flat

| Period | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |
|---|---:|---:|---:|---:|---:|
| 2000-01–2007-12 | 12 | 10 | 54.71% | 69.88% | -12.93% |
| 2008-01–2009-12 | 12 | 10 | -9.52% | -17.02% | -12.46% |
| 2010-01–2016-12 | 12 | 10 | 110.29% | 134.46% | -17.50% |

## Descriptive uncertainty

Paired circular-block percentile intervals on the aggregate annualised arithmetic mean difference (not CAGR). 2,000 resamples, seed 2026; 12 periods/year. No independent-industry or multiple-testing inference.

| Block months | Mean difference | 95% interval |
|---|---:|---:|
| 6 | -1.16% | [-5.91%, 3.51%] |
| 12 | -1.16% | [-5.30%, 3.14%] |
| 24 | -1.16% | [-4.36%, 2.36%] |

## Limitations and reproduction

These are revised historical research portfolios, not executable ETF instruments. Industry exposures are correlated. Data adjustment and current upstream revisions are not independently reconciled; checksum and calendar validation establish reproducibility and internal consistency, not independent vendor verification. The fixed history is retrospective, not genuinely unseen. Costs are illustrative and cannot reproduce trading all underlying stocks. Subperiods reset holdings and therefore are not additive components of the full history.

Source: https://raw.githubusercontent.com/bashtage/linearmodels/d7980a7dd8d7f8802e0303b5bc769abb08a3c699/linearmodels/datasets/french/french.csv.bz2

SHA-256: `fab6482f4f011a2fcec2fd087d740eef3c5bcc24a39459569a4224516fca1b6e`. Full per-industry results, aggregate return paths, audit and code hashes are retained in the adjacent JSON. Raw data is downloaded locally and not redistributed.

```bash
uv run python -m quant_research.followup --download
uv run python -m quant_research.followup
```

There were no changes to the declared dates, industry universe or fixed setting after inspecting returns. Longer data improves coverage, not evidence of a universally profitable rule.
