"""Independent accounting and timing checks for the monthly follow-up."""

from datetime import date

import pytest

from quant_research.backtest import run_backtest
from quant_research.followup import (
    INDUSTRIES,
    evaluate_period,
    load_snapshot,
    parse_returns,
)
from quant_research.study import paired_block_interval


def test_cash_compounds_at_supplied_rate_and_zero_default_unchanged():
    assert run_backtest(
        [100, 110, 121], [0, 0, 0], cash_returns=[0.01, 0.02]
    ).returns == pytest.approx([0.01, 0.02])
    assert run_backtest([100, 110, 121], [0, 0, 0]).returns == (0, 0)


def test_fractional_allocation_drift_includes_cash():
    result = run_backtest(
        [100, 120, 120], [0.5, 0.5, 0.5], 100, cash_returns=[0.1, 0.0]
    )
    first_fee = 0.01 * 0.5 / 1.005
    drifted = 0.5 * 1.2 / 1.15
    second_fee = 0.01 * (drifted - 0.5) / 0.995
    assert result.returns == pytest.approx([(1 - first_fee) * 1.15 - 1, -second_fee])


@pytest.mark.parametrize("cash", [[0], [float("nan"), 0], [-1, 0], [True, 0]])
def test_bad_cash_returns_rejected(cash):
    with pytest.raises(ValueError):
        run_backtest([100, 101, 102], [0, 0, 0], cash_returns=cash)


def sample():
    dates = [date(2000 + i // 12, i % 12 + 1, 1) for i in range(36)]
    return dates, {
        name: ([0.01] * 36 if name != "RF" else [0.001] * 36)
        for name in (*INDUSTRIES, "RF")
    }


def test_monthly_delay_and_future_invariance():
    dates, values = sample()
    # Month 15 sees the signal through month 13; month 14 shock cannot affect
    # month 15's position, but changes the signal used for month 16.
    for name in INDUSTRIES:
        values[name][14] = -0.5
    report = evaluate_period(dates, values, str(dates[15]), str(dates[20]), 3, 0)
    path = report["aggregate_returns"]["strategy"]
    assert path[0] == pytest.approx(0.01)
    assert path[1] == pytest.approx(0.001)
    for name in INDUSTRIES:
        values[name][21:] = [0.9] * 15
    assert (
        evaluate_period(dates, values, str(dates[15]), str(dates[20]), 3, 0) == report
    )


def test_equal_sleeve_aggregate_matches_identical_industries():
    dates, values = sample()
    report = evaluate_period(dates, values, str(dates[15]), str(dates[20]), 3, 10)
    assert report["aggregate"]["strategy"]["total_return"] == pytest.approx(
        report["industries"]["NoDur"]["strategy"]["total_return"]
    )


def test_bootstrap_uses_monthly_annualisation():
    result = paired_block_interval(
        [0.01] * 24, [0] * 24, periods_per_year=12, repeats=50
    )
    assert result["estimate"] == pytest.approx(0.12)
    assert result["percentile_95"] == pytest.approx([0.12, 0.12])


def test_snapshot_integrity():
    with pytest.raises(ValueError, match="SHA-256"):
        load_snapshot(b"corrupt")


@pytest.mark.parametrize(
    "months,number",
    [
        (["2000-01-01", "2000-03-01"], "0.01"),
        (["2000-01-01", "2000-01-01"], "0.01"),
        (["2000-01-01"], "-99.99"),
        (["2000-01-01"], "-0.9999"),
        (["2000-01-01"], "nan"),
    ],
)
def test_bad_calendar_and_returns_rejected(months, number):
    header = ",".join(("dates", "RF", *INDUSTRIES))
    text = header + "\n" + "\n".join(d + "," + ",".join([number] * 13) for d in months)
    with pytest.raises(ValueError):
        parse_returns(text)


def test_cash_excess_sharpe_is_undefined_despite_roundoff():
    dates, values = sample()
    values["RF"] = [0.0003 * (i % 7) for i in range(36)]
    report = evaluate_period(dates, values, str(dates[15]), str(dates[20]), 3, 10)
    assert report["aggregate"]["cash"]["sharpe_excess_cash"] is None
