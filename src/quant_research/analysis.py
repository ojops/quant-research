"""Return and risk calculations with explicit observation-frequency assumptions."""

from math import isfinite, sqrt
from statistics import mean, stdev

from quant_research.data import validate_prices


def simple_returns(prices) -> tuple[float, ...]:
    validate_prices(prices)
    values = tuple(b / a - 1 for a, b in zip(prices, prices[1:]))
    if any(not isfinite(r) or r <= -1 for r in values):
        raise ValueError("Price ratios are outside the supported floating-point range")
    return values


def equity_curve(returns) -> tuple[float, ...]:
    """Include initial wealth so losses in the first period count as drawdowns."""
    values = [1.0]
    for value in returns:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value < -1
        ):
            raise ValueError(
                "Returns must be finite numbers greater than or equal to -1"
            )
        wealth = values[-1] * (1 + value)
        if not isfinite(wealth):
            raise ValueError("Equity overflow")
        values.append(wealth)
    return tuple(values)


def performance(returns, periods_per_year=252) -> dict:
    """Sample volatility and zero-risk-free Sharpe; no inference about significance."""
    returns = tuple(returns)
    if not returns:
        raise ValueError("At least one return is required")
    if type(periods_per_year) is not int or periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")
    curve = equity_curve(returns)
    peak, drawdown = 1.0, 0.0
    for wealth in curve:
        peak = max(peak, wealth)
        drawdown = min(drawdown, wealth / peak - 1)
    volatility = stdev(returns) if len(returns) > 1 else None
    try:
        annual_return = curve[-1] ** (periods_per_year / len(returns)) - 1
    except OverflowError:
        raise ValueError(
            "Annualised return overflow; check data frequency and horizon"
        ) from None
    if not isfinite(annual_return):
        raise ValueError("Annualised return is not finite")
    return {
        "observations": len(returns),
        "total_return": curve[-1] - 1,
        "annualised_return": annual_return,
        "annualised_volatility": volatility * sqrt(periods_per_year)
        if volatility is not None
        else None,
        "sharpe_zero_rf": mean(returns) / volatility * sqrt(periods_per_year)
        if volatility
        else None,
        "max_drawdown": drawdown,
    }
