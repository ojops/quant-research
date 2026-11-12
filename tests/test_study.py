"""Checks for paired uncertainty and the historical pilot's data/timing boundaries."""

from datetime import date, timedelta

import pytest

from quant_research.data import PriceSeries
from quant_research.study import (
    audit,
    normalize_snapshot,
    paired_block_interval,
    period_run,
)


def test_identical_paired_paths_have_zero_difference_and_interval():
    path = [0.01, -0.02, 0.03, 0.0] * 10
    result = paired_block_interval(path, path, block_size=5, repeats=100)
    assert result["estimate"] == 0
    assert result["percentile_95"] == [0, 0]


def test_constant_paired_difference_and_seed_reproducibility():
    result = paired_block_interval([0.01] * 30, [0.0] * 30, repeats=100)
    assert result["percentile_95"] == pytest.approx([2.52, 2.52])
    a, b = [0.01, -0.02, 0.03] * 10, [0.0] * 30
    assert paired_block_interval(a, b, repeats=100) == paired_block_interval(
        a, b, repeats=100
    )


@pytest.mark.parametrize(
    "a,b,block",
    [([0.0], [0.0], 1), ([0.0, 0.1], [0.0], 1), ([0.0, 0.1], [0.0, 0.0], 3)],
)
def test_bootstrap_rejects_invalid_pairs(a, b, block):
    with pytest.raises(ValueError):
        paired_block_interval(a, b, block_size=block)


def test_source_mutation_is_rejected_before_parsing():
    with pytest.raises(ValueError, match="SHA-256"):
        normalize_snapshot(b"Date,AAPL.Adjusted\n2016-01-01,100\n")


def test_future_prices_do_not_change_evaluation():
    dates = tuple(date(2015, 1, 1) + timedelta(days=i) for i in range(180))
    prices = tuple(100 + i / 10 + (i % 7) for i in range(180))
    original = PriceSeries(dates, prices)
    changed = PriceSeries(dates, prices[:151] + tuple(p * 10 for p in prices[151:]))
    start, end = str(dates[80]), str(dates[150])
    assert period_run(original, start, end, 20, 10) == period_run(
        changed, start, end, 20, 10
    )


def test_audit_lists_gaps_without_filling():
    series = PriceSeries((date(2016, 1, 4), date(2016, 1, 6)), (100, 101))
    assert audit(series)["absent_weekdays"] == ["2016-01-05"]
    assert audit(series)["observations"] == 2


@pytest.mark.parametrize(
    "start,end",
    [
        ("2015-12-31", "2016-01-06"),
        ("2016-01-04", "2016-01-10"),
        ("2016-01-06", "2016-01-04"),
    ],
)
def test_period_rejects_truncation_and_reversed_bounds(start, end):
    series = PriceSeries(
        tuple(date(2016, 1, d) for d in range(4, 9)), (100, 101, 102, 103, 104)
    )
    with pytest.raises(ValueError, match="coverage"):
        period_run(series, start, end, 1, 10)


@pytest.mark.parametrize("block_size", [1, 4, 7, 23])
@pytest.mark.parametrize("periods_per_year", [12, 252])
def test_block_totals_match_direct_seeded_resampling(block_size, periods_per_year):
    import random
    from statistics import mean

    from quant_research.study import paired_block_interval

    strategy = [0.02 * ((i % 5) - 2) for i in range(23)]
    benchmark = [0.003 * (i % 3) for i in range(23)]
    differences = [a - b for a, b in zip(strategy, benchmark)]
    rng = random.Random(81)
    estimates = []
    for _ in range(200):
        sample = []
        while len(sample) < len(differences):
            start = rng.randrange(len(differences))
            sample.extend(
                differences[(start + j) % len(differences)]
                for j in range(min(block_size, len(differences) - len(sample)))
            )
        estimates.append(periods_per_year * mean(sample))
    estimates.sort()
    expected = []
    for probability in (0.025, 0.975):
        position = (len(estimates) - 1) * probability
        index = int(position)
        fraction = position - index
        expected.append(
            estimates[index] * (1 - fraction) + estimates[index + 1] * fraction
        )
    actual = paired_block_interval(
        strategy,
        benchmark,
        block_size=block_size,
        repeats=200,
        seed=81,
        periods_per_year=periods_per_year,
    )
    assert actual["percentile_95"] == pytest.approx(expected, rel=1e-13, abs=1e-14)
    assert "daily" not in actual["estimand"]
