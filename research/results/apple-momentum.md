# Historical momentum pilot: AAPL

## Question and design

Sensitivity of long-or-cash momentum to lookback and costs, relative to buy-and-hold and cash

Fixed 20-observation/10bps rule; retrospective evaluation, not a genuinely untouched holdout. No optimisation or selection. Evaluation grid is descriptive sensitivity only.

See [the protocol](../../docs/STUDY_PLAN.md), recorded before this implementation downloaded prices. All grid combinations are retained; the fixed rule was not chosen by its performance.

Evaluation: 2016-01-04 to 2016-12-30. Observations before the period supply signal warm-up only. All models start flat; the first interval includes entry costs. Subperiods restart flat and are not an additive decomposition of the full-year return.

## Fixed-rule result

| Model | Total return | Annualised volatility | Zero-RF Sharpe | Maximum drawdown | Turnover |
|---|---:|---:|---:|---:|---:|
| strategy | 8.61% | 13.66% | 0.675 | -11.69% | 21.0 |
| buy_and_hold | 12.27% | 23.40% | 0.614 | -18.92% | 1.0 |
| cash | 0.00% | 0.00% | undefined | 0.00% | 0.0 |

The fixed rule **underperformed buy-and-hold by 3.66 cumulative-return percentage points**, with shallower maximum drawdown. This is a description of one historical sample, not evidence of general predictive skill.

## Development: all declared settings

| Dates | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |
|---|---:|---:|---:|---:|---:|
| 2015-06-01 / 2015-12-31 | 5 | 0 | -8.00% | -18.65% | -11.54% |
| 2015-06-01 / 2015-12-31 | 5 | 10 | -11.87% | -18.74% | -12.77% |
| 2015-06-01 / 2015-12-31 | 5 | 50 | -25.80% | -19.06% | -25.80% |
| 2015-06-01 / 2015-12-31 | 20 | 0 | -7.40% | -18.65% | -11.83% |
| 2015-06-01 / 2015-12-31 | 20 | 10 | -9.23% | -18.74% | -13.14% |
| 2015-06-01 / 2015-12-31 | 20 | 50 | -16.21% | -19.06% | -18.20% |
| 2015-06-01 / 2015-12-31 | 60 | 0 | -10.52% | -18.65% | -11.94% |
| 2015-06-01 / 2015-12-31 | 60 | 10 | -11.94% | -18.74% | -12.90% |
| 2015-06-01 / 2015-12-31 | 60 | 50 | -17.40% | -19.06% | -17.40% |

## Evaluation sensitivity: descriptive, not new holdouts

| Dates | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |
|---|---:|---:|---:|---:|---:|
| 2016-01-04 / 2016-12-30 | 5 | 0 | -0.80% | 12.38% | -11.22% |
| 2016-01-04 / 2016-12-30 | 5 | 10 | -5.45% | 12.27% | -11.84% |
| 2016-01-04 / 2016-12-30 | 5 | 50 | -21.97% | 11.83% | -24.30% |
| 2016-01-04 / 2016-12-30 | 20 | 0 | 10.92% | 12.38% | -11.33% |
| 2016-01-04 / 2016-12-30 | 20 | 10 | 8.61% | 12.27% | -11.69% |
| 2016-01-04 / 2016-12-30 | 20 | 50 | -0.14% | 11.83% | -14.25% |
| 2016-01-04 / 2016-12-30 | 60 | 0 | 2.42% | 12.38% | -16.81% |
| 2016-01-04 / 2016-12-30 | 60 | 10 | 0.69% | 12.27% | -17.06% |
| 2016-01-04 / 2016-12-30 | 60 | 50 | -5.93% | 11.83% | -18.92% |

## Fixed-rule subperiods, each starting flat

| Dates | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |
|---|---:|---:|---:|---:|---:|
| 2016-01-04 / 2016-06-30 | 20 | 10 | -2.44% | -8.30% | -11.69% |
| 2016-07-01 / 2016-12-30 | 20 | 10 | 11.32% | 21.94% | -5.73% |

## Descriptive uncertainty

Paired circular-block bootstrap; annualised arithmetic mean daily return difference, **not CAGR difference**. Percentile intervals preserve within-block dependence but do not establish stationarity, independence, or account for strategy selection/multiple comparisons.

| Block observations | Estimate | 95% percentile interval |
|---|---:|---:|
| 5 | -5.14% | [-43.36%, 35.04%] |
| 20 | -5.14% | [-40.06%, 32.38%] |
| 60 | -5.14% | [-28.94%, 17.44%] |

## Provenance and limitations

Source: https://raw.githubusercontent.com/plotly/datasets/0c447c47b757ad74edecab31f0d72f849d2e67c2/finance-charts-apple.csv

Raw SHA-256: `24c7604edfd5afe862ddb9f9535e2fd7351f43711bfc442bca52055e15e37bcd`. JSON records the normalised checksum, implementation hashes, complete fixed-rule return paths and data audit.

The snapshot uses the vendor's AAPL.Adjusted field; split/dividend adjustments have not been independently reconstructed. Archived values are not executable prices or a point-in-time data feed. Raw prices are downloaded locally, not redistributed under the code's MIT licence.

Single retrospectively chosen surviving stock; short history; no unseen prospective evaluation; no cross-asset evidence. Later 2017 observations are excluded from every reported evaluation. The data audit lists absent weekdays without treating exchange holidays as missing data or filling them.

One-close execution delay; proportional turnover costs; no spread/impact model; zero cash/risk-free return; no forced final liquidation. A signal uses only already observed prices. Borrowing, taxes and live execution are not modelled.

The next useful step is an independently sourced, longer and broader dataset plus a genuinely prospective frozen evaluation. Do not choose a new rule from this sensitivity table and call the same period an untouched test.
