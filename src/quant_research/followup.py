"""Long-horizon monthly industry study with cash yield and a fixed protocol."""

import argparse
import bz2
import csv
import hashlib
import io
import json
import math
import platform
from datetime import date
from pathlib import Path
from statistics import mean, stdev
from urllib.request import urlopen

from quant_research.analysis import equity_curve, performance, simple_returns
from quant_research.backtest import momentum_weights, run_backtest
from quant_research.study import paired_block_interval

URL = "https://raw.githubusercontent.com/bashtage/linearmodels/d7980a7dd8d7f8802e0303b5bc769abb08a3c699/linearmodels/datasets/french/french.csv.bz2"
SHA256 = "fab6482f4f011a2fcec2fd087d740eef3c5bcc24a39459569a4224516fca1b6e"
INDUSTRIES = (
    "NoDur",
    "Durbl",
    "Manuf",
    "Enrgy",
    "Chems",
    "BusEq",
    "Telcm",
    "Utils",
    "Shops",
    "Hlth",
    "Money",
    "Other",
)


def parse_returns(text):
    """Require contiguous monthly labels and decimal returns; never fill gaps."""
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    if len(set(fields)) != len(fields) or not {"dates", "RF", *INDUSTRIES} <= set(
        fields
    ):
        raise ValueError("Expected distinct dates, RF and all 12 industry columns")
    dates, values = [], {name: [] for name in ("RF", *INDUSTRIES)}
    for row in reader:
        day = date.fromisoformat(row["dates"])
        if day.day != 1 or (
            dates
            and day.year * 12 + day.month != dates[-1].year * 12 + dates[-1].month + 1
        ):
            raise ValueError("Month labels must be contiguous, unique and increasing")
        dates.append(day)
        for name in values:
            value = float(row[name])
            # Fractional returns, not percentages. Reject common French missing codes
            # (-99.99 / -999, including after division by 100) and wrong-unit values.
            if (
                not math.isfinite(value)
                or value <= -1
                or value == -0.9999
                or abs(value) > 1
            ):
                raise ValueError(
                    f"Invalid decimal return or missing code: {name} {day}"
                )
            values[name].append(value)
    if len(dates) < 24:
        raise ValueError("Insufficient monthly history")
    return dates, values


def load_snapshot(raw):
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("Historical source SHA-256 mismatch")
    return parse_returns(bz2.decompress(raw).decode("utf-8"))


def metrics(returns, cash):
    result = performance(returns, 12)
    result.pop("sharpe_zero_rf")
    excess = [a - b for a, b in zip(returns, cash)]
    # Reconstructed cash paths differ from RF by machine roundoff only.
    volatility = stdev(excess)
    result["sharpe_excess_cash"] = (
        mean(excess) / volatility * math.sqrt(12) if volatility > 1e-12 else None
    )
    return result


def evaluate_period(dates, values, start, end, lookback=12, cost=10):
    try:
        first, last = (
            dates.index(date.fromisoformat(start)),
            dates.index(date.fromisoformat(end)),
        )
    except ValueError:
        raise ValueError("Requested period endpoints must be present") from None
    if first < lookback + 1 or last <= first:
        raise ValueError("Need prior lookback plus one-month delay and multiple months")
    cash = values["RF"][first : last + 1]
    sleeves, paths = {}, {m: [] for m in ("strategy", "buy_and_hold", "cash")}
    for name in INDUSTRIES:
        levels = equity_curve(values[name])
        signals = momentum_weights(levels, lookback)
        prices = levels[first : last + 2]
        targets = signals[first - 1 : last + 1]
        runs = {
            "strategy": run_backtest(prices, targets, cost, cash_returns=cash),
            "buy_and_hold": run_backtest(
                prices, [1.0] * len(prices), cost, cash_returns=cash
            ),
            "cash": run_backtest(prices, [0.0] * len(prices), cost, cash_returns=cash),
        }
        sleeves[name] = {}
        for model, run in runs.items():
            sleeves[name][model] = {
                **metrics(run.returns, cash),
                "turnover": sum(run.turnover),
            }
            paths[model].append(equity_curve(run.returns))
    aggregate, aggregate_paths = {}, {}
    for model, curves in paths.items():
        curve = [mean(v) for v in zip(*curves)]
        returns = simple_returns(curve)
        aggregate[model] = metrics(returns, cash)
        aggregate_paths[model] = list(returns)
    return {
        "start": start[:7],
        "end": end[:7],
        "lookback_months": lookback,
        "cost_bps": cost,
        "industries": sleeves,
        "aggregate": aggregate,
        "aggregate_returns": aggregate_paths,
    }


def without_paths(report):
    """Sensitivity tables retain all metrics; full paths are kept for the fixed run."""
    return {key: value for key, value in report.items() if key != "aggregate_returns"}


def run_followup(raw):
    dates, values = load_snapshot(raw)
    grids = {}
    for role, start, end in (
        ("development", "1980-01-01", "1999-12-01"),
        ("evaluation", "2000-01-01", "2016-12-01"),
    ):
        grids[role] = [
            evaluate_period(dates, values, start, end, lookback, cost)
            for lookback in (3, 6, 12)
            for cost in (0, 10, 50)
        ]
    fixed = next(
        r
        for r in grids["evaluation"]
        if r["lookback_months"] == 12 and r["cost_bps"] == 10
    )
    return {
        "schema_version": 1,
        "source": {
            "url": URL,
            "sha256": SHA256,
            "upstream": "Ken French data library, archived by linearmodels; not independently reconciled to today's revised upstream release",
            "units": "Monthly decimal portfolio returns; 0.01 means 1%, not 0.01%",
            "adjustments": "Research portfolio returns compounded into total-return levels; not adjusted executable prices. Dividend/corporate-action processing inherited from the archive, not independently reconstructed.",
            "rights": "Third-party data rights not inferred from code licence; raw archive stays local.",
        },
        "audit": {
            "first_month": str(dates[0]),
            "last_month": str(dates[-1]),
            "months": len(dates),
            "industries": list(INDUSTRIES),
            "checks": "Contiguous unique months, all columns, finite decimal returns, missing-code rejection, checksum, full evaluation coverage",
            "range": {k: [min(v), max(v)] for k, v in values.items()},
        },
        "design": "Fixed 12-month lookback, one-month execution delay and 10bps cost. No parameter selection. All other settings are descriptive sensitivity, not independent holdouts. Equal initial capital in 12 independent sleeves; no cross-sleeve rebalancing.",
        "python": platform.python_version(),
        "implementation_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob("*.py"))
        },
        "fixed_evaluation": fixed,
        "development": [without_paths(r) for r in grids["development"]],
        "evaluation_sensitivity": [without_paths(r) for r in grids["evaluation"]],
        "subperiods": [
            evaluate_period(dates, values, a, b)
            for a, b in (
                ("2000-01-01", "2007-12-01"),
                ("2008-01-01", "2009-12-01"),
                ("2010-01-01", "2016-12-01"),
            )
        ],
        "uncertainty": [
            paired_block_interval(
                fixed["aggregate_returns"]["strategy"],
                fixed["aggregate_returns"]["buy_and_hold"],
                block_size=b,
                periods_per_year=12,
            )
            for b in (6, 12, 24)
        ],
    }


def markdown(report):
    fixed = report["fixed_evaluation"]
    lines = [
        "# Long-horizon industry momentum follow-up",
        "",
        "## Design and data",
        "",
        report["design"],
        "",
        "[Protocol](../../docs/FOLLOWUP_PLAN.md) recorded before return inspection. Archive: 819 contiguous months, January 1949–March 2017, 12 industries. Development is 1980–1999; evaluation is 2000–2016 (204 months). Other observations provide warm-up or remain excluded. Monthly resolution is different from the daily AAPL pilot; this is not an exact replication.",
        "",
        "Cash earns contemporaneous RF. Signal through month t is traded at the end of t+1 and first earns t+2. All models start flat; buy-and-hold pays entry costs. No terminal liquidation. Sharpe uses monthly returns minus RF; volatility is sample volatility of actual returns, annualised by sqrt(12).",
        "",
        "## Fixed aggregate result",
        "",
        "| Model | Total return | Annualised return | Annualised volatility | Excess-cash Sharpe | Max drawdown |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, m in fixed["aggregate"].items():
        sharpe = (
            f"{m['sharpe_excess_cash']:.3f}"
            if m["sharpe_excess_cash"] is not None
            else "undefined"
        )
        lines.append(
            f"| {name} | {m['total_return']:.2%} | {m['annualised_return']:.2%} | {m['annualised_volatility']:.2%} | {sharpe} | {m['max_drawdown']:.2%} |"
        )
    s, b = (fixed["aggregate"][m] for m in ("strategy", "buy_and_hold"))
    lines += [
        "",
        f"Fixed-rule cumulative return minus buy-and-hold: **{100 * (s['total_return'] - b['total_return']):+.2f} percentage points**. Maximum drawdown: {s['max_drawdown']:.2%} versus {b['max_drawdown']:.2%}. This is a historical comparison, not a profitability or significance claim.",
        "",
        "## Every industry at the fixed setting",
        "",
        "| Industry | Strategy return | Buy-and-hold return | Strategy drawdown | Buy-and-hold drawdown |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, runs in fixed["industries"].items():
        s, b = (runs[m] for m in ("strategy", "buy_and_hold"))
        lines.append(
            f"| {name} | {s['total_return']:.2%} | {b['total_return']:.2%} | {s['max_drawdown']:.2%} | {b['max_drawdown']:.2%} |"
        )
    for key, title in (
        ("development", "Development grid"),
        ("evaluation_sensitivity", "Evaluation sensitivity (not fresh holdouts)"),
        ("subperiods", "Fixed-rule subperiods, each restarting flat"),
    ):
        lines += [
            "",
            f"## {title}",
            "",
            "| Period | Lookback | Cost bps | Strategy return | Buy-and-hold return | Strategy drawdown |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for r in report[key]:
            s, b = (r["aggregate"][m] for m in ("strategy", "buy_and_hold"))
            lines.append(
                f"| {r['start']}–{r['end']} | {r['lookback_months']} | {r['cost_bps']} | {s['total_return']:.2%} | {b['total_return']:.2%} | {s['max_drawdown']:.2%} |"
            )
    lines += [
        "",
        "## Descriptive uncertainty",
        "",
        "Paired circular-block percentile intervals on the aggregate annualised arithmetic mean difference (not CAGR). 2,000 resamples, seed 2026; 12 periods/year. No independent-industry or multiple-testing inference.",
        "",
        "| Block months | Mean difference | 95% interval |",
        "|---|---:|---:|",
    ]
    for r in report["uncertainty"]:
        lo, hi = r["percentile_95"]
        lines.append(
            f"| {r['block_size']} | {r['estimate']:.2%} | [{lo:.2%}, {hi:.2%}] |"
        )
    lines += [
        "",
        "## Limitations and reproduction",
        "",
        "These are revised historical research portfolios, not executable ETF instruments. Industry exposures are correlated. Data adjustment and current upstream revisions are not independently reconciled; checksum and calendar validation establish reproducibility and internal consistency, not independent vendor verification. The fixed history is retrospective, not genuinely unseen. Costs are illustrative and cannot reproduce trading all underlying stocks. Subperiods reset holdings and therefore are not additive components of the full history.",
        "",
        "Source: " + URL,
        "",
        f"SHA-256: `{SHA256}`. Full per-industry results, aggregate return paths, audit and code hashes are retained in the adjacent JSON. Raw data is downloaded locally and not redistributed.",
        "",
        "```bash",
        "uv run python -m quant_research.followup --download",
        "uv run python -m quant_research.followup",
        "```",
        "",
        "There were no changes to the declared dates, industry universe or fixed setting after inspecting returns. Longer data improves coverage, not evidence of a universally profitable rule.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument(
        "--source", type=Path, default=Path("research/local/french.csv.bz2")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("research/results/industry-momentum.json")
    )
    args = parser.parse_args()
    if args.download:
        with urlopen(URL, timeout=30) as response:
            raw = response.read()
        load_snapshot(raw)
        args.source.parent.mkdir(parents=True, exist_ok=True)
        args.source.write_bytes(raw)
        print(f"Verified snapshot: {args.source}")
        return
    report = run_followup(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    args.output.with_suffix(".md").write_text(markdown(report))
    print(args.output)


if __name__ == "__main__":
    main()
