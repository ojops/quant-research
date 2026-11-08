"""Independent accounting, chronology and experiment reproduction checks."""

import json
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

import pytest

from quant_research.analysis import equity_curve
from quant_research.backtest import run_backtest
from quant_research.data import PriceSeries
from quant_research.evaluation import evaluate
from quant_research.experiment import run_experiment
from quant_research.main import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/synthetic_experiment.json"


def series(prices):
    return PriceSeries(
        [date(2024, 1, 1) + timedelta(days=i) for i in range(len(prices))], prices
    )


def test_fractional_accounting_matches_independent_cash_and_shares_ledger():
    prices = [100, 150, 90, 120, 110]
    weights = [Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), Fraction(0), Fraction(1)]
    rate = Fraction(1, 100)
    cash, shares = Fraction(1), Fraction(0)
    wealth = [Fraction(1)]
    for price, next_price, weight in zip(prices, prices[1:], weights):
        before = cash + shares * price
        # Solve for purchased/sold shares using the post-fee target allocation.
        direction = 1 if weight * before >= shares * price else -1
        new_shares = (
            weight
            * (before + direction * rate * shares * price)
            / (price * (1 + direction * rate * weight))
        )
        trade = (new_shares - shares) * price
        cash -= trade + rate * abs(trade)
        shares = new_shares
        assert cash >= 0
        wealth.append(cash + shares * next_price)
    result = run_backtest(prices, [float(w) for w in weights], cost_bps=100)
    assert equity_curve(result.returns) == pytest.approx([float(w) for w in wealth])
    assert result.positions[-1] == 0  # Final unobservable target is never executed.


def test_next_close_does_not_capture_signal_or_execution_interval():
    data = series([100, 100, 200, 300, 150, 150])
    report = evaluate(data, data.dates[2], lookback=1, cost_bps=0, execution_lag=1)
    assert report["strategy"]["path"]["positions"] == (0, 1, 1)
    assert report["strategy"]["path"]["returns"] == pytest.approx([0, -0.5, 0])
    assert report["signal_dates"] == [str(d) for d in data.dates[1:4]]
    assert len(report["valuation_dates"]) == 4
    assert report["cash"]["path"]["returns"] == (0, 0, 0)
    assert report["cash"]["total_turnover"] == 0
    assert report["cash"]["metrics"]["sharpe_zero_rf"] is None


@pytest.mark.parametrize("lag", [0, 1])
def test_future_prices_cannot_change_earlier_positions_or_returns(lag):
    original = series([100, 101, 99, 102, 104, 103, 109])
    changed = series([100, 101, 99, 102, 104, 1000, 1])
    kwargs = dict(start=original.dates[2], lookback=1, execution_lag=lag)
    first, second = evaluate(original, **kwargs), evaluate(changed, **kwargs)
    # The close at index 5 can first change the return ending there.
    for model in ("strategy", "buy_and_hold", "cash"):
        for field in ("returns", "positions", "costs", "turnover"):
            assert first[model]["path"][field][:2] == second[model]["path"][field][:2]
    end = original.dates[4]
    assert evaluate(original, end=end, **kwargs) == evaluate(changed, end=end, **kwargs)


def test_end_date_is_inclusive_and_all_models_start_flat():
    data = series([100, 101, 102, 103, 104, 105])
    result = evaluate(data, data.dates[2], end=data.dates[4], lookback=1, cost_bps=100)
    for model in ("strategy", "buy_and_hold", "cash"):
        assert result[model]["metrics"]["observations"] == 2
    assert result["buy_and_hold"]["path"]["costs"][0] == pytest.approx(0.01 / 1.01)
    assert result["buy_and_hold"]["path"]["costs"][1] == 0
    assert result["cash"]["metrics"]["total_return"] == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"lookback": 2, "execution_lag": 1},
        {"lookback": 1, "end": date(2024, 1, 4)},
        {"lookback": 1, "end": date(2024, 2, 1)},
        {"lookback": 1, "execution_lag": True},
    ],
)
def test_invalid_horizon_or_lag_is_rejected(kwargs):
    data = series([100, 101, 102, 103, 104])
    with pytest.raises(ValueError):
        evaluate(data, data.dates[2], **kwargs)


def copy_experiment(tmp_path):
    config = json.loads(EXAMPLE.read_text())
    (tmp_path / "synthetic_prices.csv").write_bytes(
        EXAMPLE.with_name("synthetic_prices.csv").read_bytes()
    )
    path = tmp_path / "experiment.json"
    path.write_text(json.dumps(config))
    return path, config


def test_experiment_repeats_exactly_and_resolves_relative_paths(tmp_path, monkeypatch):
    path, config = copy_experiment(tmp_path)
    monkeypatch.chdir(tmp_path.parent)
    output = run_experiment(path)
    assert output == run_experiment(path)
    assert len(output["runs"]) == 9
    assert len(output["comparison"]) == 27
    assert output["configuration"] == config
    assert all(
        run["test_start"] == "2024-02-01" and run["test_end"] == "2024-03-22"
        for run in output["runs"]
    )
    assert all(len(run["strategy"]["path"]["returns"]) == 36 for run in output["runs"])
    assert "backtest.py" in output["implementation_sha256"]
    assert len(output["configuration_sha256"]) == 64


def test_checksum_mismatch_rejected_before_reporting(tmp_path):
    path, _ = copy_experiment(tmp_path)
    with (tmp_path / "synthetic_prices.csv").open("a") as handle:
        handle.write("\n")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        run_experiment(path)


def test_declared_holdout_disallows_sensitivity(tmp_path):
    path, config = copy_experiment(tmp_path)
    config["evaluation"]["role"] = "declared_holdout"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="one lookback"):
        run_experiment(path)
    config["parameters"]["lookbacks"] = [5]
    config["parameters"]["cost_bps"] = [10]
    path.write_text(json.dumps(config))
    assert len(run_experiment(path)["runs"]) == 1


def test_config_typo_duplicate_and_cli_overrides_are_rejected(tmp_path, capsys):
    path, config = copy_experiment(tmp_path)
    config["parameters"]["lookbak"] = 5
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="exactly"):
        run_experiment(path)
    path.write_text('{"name": "one", "name": "two"}')
    with pytest.raises(ValueError, match="Duplicate"):
        run_experiment(path)
    with pytest.raises(SystemExit) as error:
        main(["--experiment", str(EXAMPLE), "--lookback", "5"])
    assert error.value.code == 2
    assert not capsys.readouterr().out


def test_experiment_cli_is_machine_readable_and_reproducible(capsys):
    assert main(["--experiment", str(EXAMPLE)]) == 0
    first = capsys.readouterr().out
    assert main(["--experiment", str(EXAMPLE)]) == 0
    assert first == capsys.readouterr().out
    assert (
        json.loads(first)["configuration"]["data"]["provenance"]["kind"] == "synthetic"
    )
