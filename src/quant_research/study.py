"""Fixed retrospective AAPL pilot; no parameter selection or profitability claim."""

import argparse
import csv
import hashlib
import io
import json
import platform
import random
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

from quant_research.data import PriceSeries, parse_prices
from quant_research.evaluation import evaluate

SOURCE_URL = (
    "https://raw.githubusercontent.com/plotly/datasets/"
    "0c447c47b757ad74edecab31f0d72f849d2e67c2/finance-charts-apple.csv"
)
SOURCE_SHA256 = "24c7604edfd5afe862ddb9f9535e2fd7351f43711bfc442bca52055e15e37bcd"


def normalize_snapshot(raw: bytes) -> str:
    """Verify immutable source bytes before selecting vendor-adjusted prices."""
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Historical source SHA-256 mismatch")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["date", "adjusted_close"])
    for row in reader:
        writer.writerow([row["Date"], row["AAPL.Adjusted"]])
    text = output.getvalue()
    parse_prices(text)
    return text


def paired_block_interval(
    strategy, benchmark, *, block_size=20, repeats=2000, seed=2026
):
    """Circular paired block bootstrap of annualised arithmetic mean difference.

    Blocks preserve local serial dependence, not structural breaks. Intervals
    are descriptive percentile intervals, not multiplicity-adjusted inference.
    """
    if len(strategy) != len(benchmark) or len(strategy) < 2:
        raise ValueError("Paired return arrays must have equal length >= 2")
    if type(block_size) is not int or not 1 <= block_size <= len(strategy):
        raise ValueError("block_size must be an integer within the sample length")
    if type(repeats) is not int or repeats < 2:
        raise ValueError("repeats must be an integer >= 2")
    # Existing validation rejects NaN, infinities and invalid return domains.
    from quant_research.analysis import equity_curve

    equity_curve(strategy)
    equity_curve(benchmark)
    differences = [a - b for a, b in zip(strategy, benchmark)]
    n = len(differences)
    rng = random.Random(seed)
    estimates = []
    for _ in range(repeats):
        sample = []
        while len(sample) < n:
            start = rng.randrange(n)
            sample.extend(
                differences[(start + j) % n]
                for j in range(min(block_size, n - len(sample)))
            )
        estimates.append(252 * mean(sample))
    estimates.sort()

    def percentile(p):
        position = (len(estimates) - 1) * p
        lower = int(position)
        fraction = position - lower
        return (
            estimates[lower] * (1 - fraction)
            + estimates[min(lower + 1, len(estimates) - 1)] * fraction
        )

    return {
        "estimand": "annualised arithmetic mean strategy-minus-buy-and-hold daily return; not CAGR",
        "estimate": 252 * mean(differences),
        "percentile_95": [percentile(0.025), percentile(0.975)],
        "block_size": block_size,
        "replications": repeats,
        "seed": seed,
    }


def audit(series: PriceSeries):
    """List absent weekdays, without confusing exchange holidays with bad data."""
    present = set(series.dates)
    day = series.dates[0]
    absent = []
    while day <= series.dates[-1]:
        if day.weekday() < 5 and day not in present:
            absent.append(str(day))
        day += timedelta(days=1)
    return {
        "observations": len(series.dates),
        "start": str(series.dates[0]),
        "end": str(series.dates[-1]),
        "absent_weekdays": absent,
        "weekend_observations": [str(d) for d in series.dates if d.weekday() >= 5],
        "note": "Dates unique/increasing and prices positive/finite. No filling. Absent weekdays may be holidays; exchange-calendar completeness is not independently verified.",
    }


def period_run(series, start, end, lookback, cost):
    available = [
        d
        for d in series.dates
        if date.fromisoformat(start) <= d <= date.fromisoformat(end)
    ]
    if len(available) < 3:
        raise ValueError("Insufficient observations in requested period")
    return evaluate(
        series,
        available[0],
        end=available[-1],
        lookback=lookback,
        cost_bps=cost,
        execution_lag=1,
    )


def compact(run):
    return {
        "start": run["test_start"],
        "end": run["test_end"],
        **run["settings"],
        **{
            model: {
                "metrics": run[model]["metrics"],
                "total_turnover": run[model]["total_turnover"],
            }
            for model in ("strategy", "buy_and_hold", "cash")
        },
    }


def run_study(raw: bytes):
    normalized = normalize_snapshot(raw)
    series = parse_prices(normalized)
    fixed = period_run(series, "2016-01-01", "2016-12-31", 20, 10)
    grids = {}
    for name, start, end in (
        ("development", "2015-06-01", "2015-12-31"),
        ("evaluation_sensitivity", "2016-01-01", "2016-12-31"),
    ):
        grids[name] = [
            compact(period_run(series, start, end, lookback, cost))
            for lookback in (5, 20, 60)
            for cost in (0, 10, 50)
        ]
    return {
        "schema_version": 1,
        "question": "Sensitivity of long-or-cash momentum to lookback and costs, relative to buy-and-hold and cash",
        "design": "Fixed 20-observation/10bps rule; retrospective evaluation, not a genuinely untouched holdout. No optimisation or selection. Evaluation grid is descriptive sensitivity only.",
        "source": {
            "url": SOURCE_URL,
            "sha256": SOURCE_SHA256,
            "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
            "field": "AAPL.Adjusted",
            "adjustments": "Vendor-adjusted price field; dividends/splits not independently reconstructed. No additional adjustments applied.",
            "licence": "Third-party financial data rights not verified; raw/normalised prices are not redistributed in this repository.",
        },
        "python_version": platform.python_version(),
        "implementation_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob("*.py"))
        },
        "data_audit": audit(series),
        "fixed_evaluation": compact(fixed),
        "fixed_evaluation_path": {
            "valuation_dates": fixed["valuation_dates"],
            "signal_dates": fixed["signal_dates"],
            **{m: fixed[m]["path"] for m in ("strategy", "buy_and_hold", "cash")},
        },
        "development": grids["development"],
        "evaluation_sensitivity": grids["evaluation_sensitivity"],
        "subperiods": [
            compact(period_run(series, start, end, 20, 10))
            for start, end in (
                ("2016-01-01", "2016-06-30"),
                ("2016-07-01", "2016-12-31"),
            )
        ],
        "uncertainty": [
            paired_block_interval(
                fixed["strategy"]["path"]["returns"],
                fixed["buy_and_hold"]["path"]["returns"],
                block_size=b,
            )
            for b in (5, 20, 60)
        ],
        "execution": fixed["execution_details"],
    }


def markdown(report):
    fixed = report["fixed_evaluation"]
    s, b = (fixed[m]["metrics"] for m in ("strategy", "buy_and_hold"))
    lines = [
        "# Historical momentum pilot: AAPL",
        "",
        "## Question and design",
        "",
        report["question"],
        "",
        report["design"],
        "",
        "See [the protocol](../../docs/STUDY_PLAN.md), recorded before this implementation downloaded prices. All grid combinations are retained; the fixed rule was not chosen by its performance.",
        "",
        f"Evaluation: {fixed['start']} to {fixed['end']}. Observations before the period supply signal warm-up only. All models start flat; the first interval includes entry costs. Subperiods restart flat and are not an additive decomposition of the full-year return.",
        "",
        "## Fixed-rule result",
        "",
        "| Model | Total return | Annualised volatility | Zero-RF Sharpe | Maximum drawdown | Turnover |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model in ("strategy", "buy_and_hold", "cash"):
        item = fixed[model]
        m = item["metrics"]
        sharpe = (
            f"{m['sharpe_zero_rf']:.3f}"
            if m["sharpe_zero_rf"] is not None
            else "undefined"
        )
        lines.append(
            f"| {model} | {m['total_return']:.2%} | {m['annualised_volatility']:.2%} | {sharpe} | {m['max_drawdown']:.2%} | {item['total_turnover']:.1f} |"
        )
    relation = (
        "underperformed" if s["total_return"] < b["total_return"] else "outperformed"
    )
    drawdown = (
        "shallower" if s["max_drawdown"] > b["max_drawdown"] else "equal or deeper"
    )
    lines += [
        "",
        f"The fixed rule **{relation} buy-and-hold by {100 * abs(s['total_return'] - b['total_return']):.2f} cumulative-return percentage points**, with {drawdown} maximum drawdown. This is a description of one historical sample, not evidence of general predictive skill.",
        "",
    ]
    for name, title in (
        ("development", "Development: all declared settings"),
        (
            "evaluation_sensitivity",
            "Evaluation sensitivity: descriptive, not new holdouts",
        ),
        ("subperiods", "Fixed-rule subperiods, each starting flat"),
    ):
        lines += [
            f"## {title}",
            "",
            "| Dates | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for row in report[name]:
            sm, bm = row["strategy"]["metrics"], row["buy_and_hold"]["metrics"]
            lines.append(
                f"| {row['start']} / {row['end']} | {row['lookback']} | {row['cost_bps']} | {sm['total_return']:.2%} | {bm['total_return']:.2%} | {sm['max_drawdown']:.2%} |"
            )
        lines.append("")
    lines += [
        "## Descriptive uncertainty",
        "",
        "Paired circular-block bootstrap; annualised arithmetic mean daily return difference, **not CAGR difference**. Percentile intervals preserve within-block dependence but do not establish stationarity, independence, or account for strategy selection/multiple comparisons.",
        "",
        "| Block observations | Estimate | 95% percentile interval |",
        "|---|---:|---:|",
    ]
    for item in report["uncertainty"]:
        lo, hi = item["percentile_95"]
        lines.append(
            f"| {item['block_size']} | {item['estimate']:.2%} | [{lo:.2%}, {hi:.2%}] |"
        )
    lines += [
        "",
        "## Provenance and limitations",
        "",
        f"Source: {SOURCE_URL}",
        "",
        f"Raw SHA-256: `{SOURCE_SHA256}`. JSON records the normalised checksum, implementation hashes, complete fixed-rule return paths and data audit.",
        "",
        "The snapshot uses the vendor's AAPL.Adjusted field; split/dividend adjustments have not been independently reconstructed. Archived values are not executable prices or a point-in-time data feed. Raw prices are downloaded locally, not redistributed under the code's MIT licence.",
        "",
        "Single retrospectively chosen surviving stock; short history; no unseen prospective evaluation; no cross-asset evidence. Later 2017 observations are excluded from every reported evaluation. The data audit lists absent weekdays without treating exchange holidays as missing data or filling them.",
        "",
        "One-close execution delay; proportional turnover costs; no spread/impact model; zero cash/risk-free return; no forced final liquidation. A signal uses only already observed prices. Borrowing, taxes and live execution are not modelled.",
        "",
        "The next useful step is an independently sourced, longer and broader dataset plus a genuinely prospective frozen evaluation. Do not choose a new rule from this sensitivity table and call the same period an untouched test.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=Path("research/local/finance-charts-apple.csv")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("research/results/apple-momentum.json")
    )
    args = parser.parse_args()
    report = run_study(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    args.output.with_suffix(".md").write_text(markdown(report))
    print(args.output)


if __name__ == "__main__":
    main()
