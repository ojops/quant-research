# Fixed long-horizon follow-up protocol

Recorded before inspecting return observations or calculating results.

Question: does the return/drawdown trade-off in the AAPL pilot persist across
longer monthly histories and diversified industry portfolios?

Source: the archived Ken French monthly return dataset distributed with
`bashtage/linearmodels`, commit d7980a7dd8d7f8802e0303b5bc769abb08a3c699,
`linearmodels/datasets/french/french.csv.bz2`. Source documentation identifies
12 industry portfolios, market excess return and the risk-free rate. Verify units,
month coverage, missing-value codes and finite returns before evaluation.
Use all 12 industry portfolios rather than choose successful industries.

Development: January 1980–December 1999. Evaluation: January 2000–December 2016.
Reject missing months or incomplete requested coverage; do not silently shorten.
Fixed rule: positive trailing 12-month total return means long; otherwise cash.
Use a one-month execution delay: a close-t signal is traded at close t+1 and
first earns month t+2. Report all 3/6/12-month lookbacks and 0/10/50 bps costs,
with the fixed 12-month/10-bps rule distinguished from descriptive sensitivity.
Cash earns the supplied monthly RF. Buy-and-hold pays the same entry cost.
Account for portfolio-weight drift and turnover costs; no final liquidation.

Report full-period performance and the fixed rule over 2000–2007, 2008–2009,
and 2010–2016, restarting in cash for each period. Build an equal-initial-capital
aggregate of the 12 independent sleeves (no cross-sleeve rebalancing).
Use the aggregate for paired circular-block bootstrap intervals of annualised
arithmetic mean strategy-minus-buy-and-hold return, block sizes 6/12/24 months,
2,000 replications, seed 2026. No winning-rule selection or significance claims.

These are research portfolio returns, not executable ETF prices. Total-return
levels will be reconstructed for momentum; no OHLC/volume or corporate-action
reconstruction is implied. This retrospective archive is revised historical data,
not a point-in-time database or a genuinely unseen prospective holdout.
The dataset has broader coverage than a surviving single stock, but portfolios
share exposures and are not 12 independent statistical replications. Keep all
results, data provenance and uncertainty. Raw third-party data remains local.
Document any protocol deviations explicitly instead of rewriting this plan.
