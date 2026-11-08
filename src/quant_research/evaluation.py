"""Compare fixed rules on an explicit, common valuation horizon."""

from dataclasses import asdict
from datetime import date

from quant_research.analysis import performance
from quant_research.backtest import momentum_weights, run_backtest
from quant_research.data import PriceSeries


def evaluate(
    series: PriceSeries,
    start: date,
    *,
    end: date | None = None,
    lookback: int = 5,
    cost_bps: float = 10,
    periods_per_year: int = 252,
    execution_lag: int = 0,
) -> dict:
    """Start flat and evaluate inclusive valuation dates, with prior warm-up.

    Lag 0 fills at the signal close (idealised); lag 1 fills at the next observed
    close and earns only the subsequent interval. Buy-and-hold is predeclared
    and enters at the first valuation date in either mode.
    """
    if type(execution_lag) is not int or execution_lag not in (0, 1):
        raise ValueError("execution_lag must be 0 (signal close) or 1 (next close)")
    signals = momentum_weights(series.prices, lookback)
    try:
        first = series.dates.index(start)
        last = series.dates.index(end) if end is not None else len(series.dates) - 1
    except ValueError:
        raise ValueError("Evaluation start and end must occur in the CSV") from None
    if first < lookback + execution_lag or last - first < 2:
        raise ValueError(
            "Evaluation needs prior lookback plus execution-lag history "
            "and at least three prices"
        )
    prices = series.prices[first : last + 1]
    targets = signals[first - execution_lag : last + 1 - execution_lag]

    def report(weights):
        result = run_backtest(prices, weights, cost_bps)
        return {
            "metrics": performance(result.returns, periods_per_year),
            "total_turnover": sum(result.turnover),
            "path": asdict(result),
        }

    return {
        "settings": {
            "lookback": lookback,
            "cost_bps": cost_bps,
            "periods_per_year": periods_per_year,
            "execution_lag": execution_lag,
        },
        "history_observations": first,
        "test_start": str(series.dates[first]),
        "test_end": str(series.dates[last]),
        "valuation_dates": [str(day) for day in series.dates[first : last + 1]],
        "signal_dates": [
            str(day)
            for day in series.dates[first - execution_lag : last - execution_lag]
        ],
        "assumptions": "Single asset, adjusted prices, zero cash/risk free rate, close execution, and no final liquidation",
        "execution_details": {
            "execution": "idealised_signal_close"
            if execution_lag == 0
            else "next_observed_close",
            "cash_and_risk_free_rate": 0,
            "initial_position": "cash for every strategy and benchmark",
            "buy_and_hold_entry": "first valuation close, predeclared",
            "final_liquidation": False,
            "price_basis": "supplied adjusted close; no adjustment or missing-session filling",
            "evaluation": "chronological; not proof of an untouched holdout",
        },
        "strategy": report(targets),
        "buy_and_hold": report([1.0] * len(prices)),
        "cash": report([0.0] * len(prices)),
    }
