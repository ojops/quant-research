# Research and accounting notes

## Returns and risk

Simple return r_t=p_t/p_(t-1)-1. Wealth compounds as V_t=V_(t-1)*(1+r_t);
returns must not be summed to obtain a multi-period return. The equity curve
includes initial wealth 1 so a first-period loss appears in drawdown.
Drawdown at t is V_t/max(V_0,...,V_t)-1; maximum drawdown is the most negative
value. It is reported as a negative fraction.

For n observed intervals and K intervals/year, the annualised compound return is
(V_n/V_0)^(K/n)-1. Annualised volatility is sample stdev(r)*sqrt(K). The reported
Sharpe is mean(r)/sample_stdev(r)*sqrt(K), with zero risk-free return assumed.
Zero sample volatility or fewer than two returns produces null Sharpe. A single
return still permits total return and drawdown. These are descriptive statistics,
not confidence intervals. Short-sample annualisation can be misleading.

## Timing and transaction costs

A target w_t computed from prices through close t is applied to t->t+1, never
the return ending at t. Future data extension must not change earlier targets.
The code tests this causality property and a 100% price jump that cannot be
captured by the signal it creates. The signal-close execution assumption is
explicitly idealised; realistic next-session fills require another price series.

Even a constant target fraction needs rebalancing after price movement. Before
the next trade, a position with target w and asset return r has weight
x=w*(1+r)/(1+w*r). Using only changes in target weights would miss that turnover.

Let c be proportional cost, x the current asset fraction of pretrade wealth, and
w the desired fraction of post-cost wealth. The cost fraction f solves
f=c*abs(w*(1-f)-x). For buys f=c*(w-x)/(1+c*w); for sells
f=c*(x-w)/(1-c*w). Actual turnover is abs(w*(1-f)-x).
Net interval return is (1-f)*(1+w*r)-1. This accounts for the fact that fees
reduce the capital available for investment. For flat prices, full entry then
exit leaves wealth (1-c)/(1+c), not exactly (1-c)^2.

Tests cover this identity, drift-aware rebalancing, zero-cost buy-and-hold
matching the underlying price ratio, causality, data rejection, drawdown and
reproducible CLI results. The implementation exposes the path rather than only
a headline score so accounting can be inspected independently.

## A defensible next experiment

1. Select an asset/universe and economic question before looking at results.
2. Record source, licence, adjustment convention, retrieval date, checksum,
   trading calendar, missing observations and any selection/survivorship limits.
3. Freeze a historical development period, validation process and final holdout.
   The current CLI uses earlier data as warm-up only; it is not a model-fitting
   framework. Test-start selection is explicit, not automatically optimised.
4. Compare predeclared buy-and-hold and cash baselines, plus cost sensitivity.
5. Report uncertainty using methods compatible with serial dependence (e.g.
   block bootstrap), and report all tried variants to expose multiple testing.

Defer portfolios, live execution and machine-learning models until those data
and experimental contracts are established. Standard-library loops are suitable
for this one-asset daily baseline; there is no measured need for vectorisation
or a distributed engine. Statistical plots and multi-asset research would justify
carefully selected scientific dependencies later, rather than now.
