# Fixed historical pilot plan

Recorded before downloading prices or computing this study's results. This is a
retrospective historical pilot, not an independently preregistered or genuinely
unseen test: AAPL and these market years are publicly known. No parameter will be
selected by its evaluation performance.

Question: how sensitive is a long-or-cash momentum rule to lookback and costs,
and does a fixed rule improve return or drawdown relative to buy-and-hold?

- Source: Plotly's archived `finance-charts-apple.csv`, immutable repository commit
  `0c447c47b757ad74edecab31f0d72f849d2e67c2`; use `Date` and `AAPL.Adjusted`.
- Development: first available session on/after 2015-06-01 through 2015-12-31.
- Evaluation: first available session on/after 2016-01-01 through 2016-12-31.
- Fixed evaluation setting: 20-observation momentum, 10 basis points per unit
  turnover, one-observation execution lag. This is chosen for simplicity, not
  selected from development returns. Report all development combinations of
  lookbacks 5/20/60 and costs 0/10/50 bps without ranking or selecting a winner.
- Report all nine combinations on evaluation too, explicitly as post-evaluation
  sensitivity analysis, not additional untouched tests. Report the fixed rule
  on each calendar half of 2016, restarting flat in each subperiod.
- Compare return, annualised volatility, zero-risk-free Sharpe, maximum drawdown
  and turnover against buy-and-hold and zero-return cash on matching dates.
- Descriptive uncertainty: paired circular-block bootstrap of daily strategy
  minus buy-and-hold returns, block sizes 5/20/60, 2,000 replications, seed 2026.
  Report percentile intervals for the annualised arithmetic mean difference;
  not CAGR, a significance test, or an adjustment for multiple comparisons.
- Audit duplicate/invalid dates and prices, weekday gaps, and observed range;
  report gaps without filling or assuming they are missing trading sessions.

Adjusted prices are vendor-supplied and corporate actions are not independently
reconstructed. The archive's redistribution rights must not be assumed from a
code licence; download the snapshot locally rather than commit raw prices.
One retrospectively chosen survivor and a short period cannot establish general
profitability. Fixed historical periods do not prove independence. Cash earns
zero; price fills, spread and market impact remain simplified. Keep all results,
including negative findings. Do not alter this plan after looking at results;
record any necessary deviations separately.
