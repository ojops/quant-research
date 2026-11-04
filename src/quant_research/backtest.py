"""A transparent close to close, long only, single asset research baseline"""

from dataclasses import dataclass
from math import isfinite

from quant_research.analysis import simple_returns
from quant_research.data import validate_prices


@dataclass(frozen=True)
class BacktestResult:
    returns: tuple[float, ...]
    positions: tuple[float, ...]
    turnover: tuple[float, ...]
    costs: tuple[float, ...]


def momentum_weights(prices, lookback=5) -> tuple[float, ...]:
    """At close t, use only prices through t, warm up remains in cash"""
    validate_prices(prices)
    if type(lookback) is not int or lookback < 1:
        raise ValueError("lookback must be a positive integer")

    return tuple(
        float(i >= lookback and prices[i] > prices[i - lookback])
        for i in range(len(prices))
    )


def run_backtest(prices, targets, cost_bps=0.0) -> BacktestResult:
    """
    Target at close t earns the return from t to t+1, after entry costs
    Targets are fractions of post cost equity
    Cash earns zero
    Fees include a constant proportional slippage assumption, no final forced liquidation
    """
    asset_returns = simple_returns(prices)
    targets = tuple(targets)
    if len(targets) != len(prices):
        raise ValueError(
            "Provide one target per price, the last has no observed future return"
        )

    if any(
        isinstance(w, bool)
        or not isinstance(w, (int, float))
        or not isfinite(w)
        or not 0 <= w <= 1
        for w in targets
    ):
        raise ValueError("Targets must be finite long-only weights between 0 and 1")

    if (
        isinstance(cost_bps, bool)
        or not isinstance(cost_bps, (int, float))
        or not isfinite(cost_bps)
        or not 0 <= cost_bps < 10_000
    ):
        raise ValueError("cost_bps must be finite and in [0, 10000)")

    rate = cost_bps / 10_000
    drifted = 0.0
    returns, positions, turnover, costs = [], [], [], []

    for target, asset_return in zip(targets, asset_returns):
        # Solve fee = rate * abs(target * (1 - fee) - drifted)
        denominator = 1 + rate * target if target >= drifted else 1 - rate * target
        fee = rate * abs(target - drifted) / denominator
        traded = abs(target * (1 - fee) - drifted)
        gross = 1 + target * asset_return

        returns.append((1 - fee) * gross - 1)
        positions.append(target)
        turnover.append(traded)
        costs.append(fee)

        drifted = target * (1 + asset_return) / gross

    return BacktestResult(
        tuple(returns), tuple(positions), tuple(turnover), tuple(costs)
    )
