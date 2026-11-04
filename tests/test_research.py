import json
from pathlib import Path

import pytest

from quant_research.analysis import equity_curve, performance, simple_returns
from quant_research.backtest import momentum_weights, run_backtest
from quant_research.data import load_prices
from quant_research.main import main


def test_returns_compound_and_drawdown_includes_initial_capital():
    returns = simple_returns([100, 110, 99])
    assert returns == pytest.approx([0.1, -0.1])
    assert equity_curve(returns)[-1] == pytest.approx(0.99)
    result = performance(returns, periods_per_year=2)
    assert result["total_return"] == pytest.approx(-0.01)
    assert result["annualised_return"] == pytest.approx(-0.01)
    assert result["max_drawdown"] == pytest.approx(-0.1)
    assert performance([-0.1])["max_drawdown"] == pytest.approx(-0.1)
    assert performance([0, 0])["sharpe_zero_rf"] is None
    assert performance([-1, 0])["total_return"] == -1


@pytest.mark.parametrize(
    "prices", [[100, 0], [100, -1], [100, float("nan")], [100, float("inf")], [100]]
)
def test_bad_prices_are_rejected(prices):
    with pytest.raises(ValueError):
        simple_returns(prices)


@pytest.mark.parametrize(
    "text",
    [
        "date,adjusted_close\n2024-01-02,100\n2024-01-01,101\n",
        "date,adjusted_close\n2024-01-01,100\n2024-01-01,101\n",
        "date,close\n2024-01-01,100\n",
        "date,adjusted_close\n2024-01-01,NaN\n2024-01-02,100\n",
        "date,adjusted_close\n2024-01-01,100,extra\n2024-01-02,101\n",
    ],
)
def test_invalid_csv_is_rejected(tmp_path, text):
    path = tmp_path / "prices.csv"
    path.write_text(text)
    with pytest.raises(ValueError):
        load_prices(path)


def test_signals_do_not_earn_the_return_that_created_them():
    prices = [100, 200, 200]
    weights = momentum_weights(prices, 1)
    assert weights == (0, 1, 0)
    assert run_backtest(prices, weights).returns == (0, 0)
    assert momentum_weights(prices + [10, 1000], 1)[:3] == weights


def test_buy_and_hold_matches_price_ratio_without_costs():
    prices = [100, 110, 90, 120]
    result = run_backtest(prices, [1.0] * 4)
    assert equity_curve(result.returns)[-1] == pytest.approx(1.2)
    assert result.turnover == pytest.approx([1, 0, 0])


def test_costs_are_self_financing_and_include_entry_and_exit():
    rate = 0.01
    result = run_backtest([100, 100, 100], [1, 0, 0], cost_bps=100)
    assert equity_curve(result.returns)[-1] == pytest.approx((1 - rate) / (1 + rate))
    assert result.costs == pytest.approx([rate / (1 + rate), rate])
    assert result.costs == pytest.approx([rate * t for t in result.turnover])


def test_rebalancing_accounts_for_drift_in_asset_weight():
    result = run_backtest([100, 200, 200], [0.5, 0.5, 0.5], 100)
    # Following the doubling, the stock weight is 2/3, not 1/2.
    assert result.costs[1] == pytest.approx(0.01 * (2 / 3 - 0.5) / (1 - 0.01 * 0.5))


@pytest.mark.parametrize(
    "weights,cost", [([0, 2], 0), ([0, float("nan")], 0), ([0, 1], -1), ([0, 1], 10000)]
)
def test_invalid_backtest_parameters(weights, cost):
    with pytest.raises(ValueError):
        run_backtest([100, 101], weights, cost)


def test_cli_reproduces_holdout_and_benchmark(capsys):
    path = Path(__file__).resolve().parents[1] / "examples/synthetic_prices.csv"
    args = [str(path), "--test-start", "2024-02-01"]
    assert main(args) == 0
    first = capsys.readouterr().out
    assert main(args) == 0
    assert capsys.readouterr().out == first
    output = json.loads(first)
    assert output["history_observations"] > 0
    assert (
        output["strategy"]["metrics"]["observations"]
        == output["buy_and_hold"]["metrics"]["observations"]
    )
    assert len(output["input_sha256"]) == 64


def test_price_series_does_not_alias_mutable_input():
    from datetime import date

    from quant_research.data import PriceSeries

    prices = [100, 101]
    series = PriceSeries([date(2024, 1, 1), date(2024, 1, 2)], prices)
    prices[0] = -1
    assert series.prices == (100, 101)
