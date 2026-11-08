"""Cost-aware, close-to-close backtesting for one long-only asset."""

from dataclasses import dataclass
from math import isfinite

from quant_research.analysis import return_from_growth, simple_returns
from quant_research.data import validate_prices


@dataclass(frozen=True)
class BacktestResult:
    returns: tuple[float, ...]
    positions: tuple[float, ...]
    turnover: tuple[float, ...]
    costs: tuple[float, ...]


def momentum_weights(prices, lookback=5) -> tuple[float, ...]:
    """Set momentum targets using prices available through each close."""
    validate_prices(prices)
    if type(lookback) is not int or lookback < 1:
        raise ValueError("lookback must be a positive integer")

    return tuple(
        float(i >= lookback and prices[i] > prices[i - lookback])
        for i in range(len(prices))
    )


def run_backtest(prices, targets, cost_bps=0.0) -> BacktestResult:
    """Backtest next-interval positions using post-cost target weights.

    Cash earns zero. Trading costs use a constant proportional rate; no final
    liquidation is forced.
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
        or not 0 <= w <= 1
        or not isfinite(w)
        for w in targets
    ):
        raise ValueError("Targets must be finite long-only weights between 0 and 1")

    if (
        isinstance(cost_bps, bool)
        or not isinstance(cost_bps, (int, float))
        or not 0 <= cost_bps < 10_000
        or not isfinite(cost_bps)
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

        returns.append(return_from_growth((1 - fee) * gross))
        positions.append(target)
        turnover.append(traded)
        costs.append(fee)

        drifted = target * (1 + asset_return) / gross

    return BacktestResult(
        tuple(returns), tuple(positions), tuple(turnover), tuple(costs)
    )
