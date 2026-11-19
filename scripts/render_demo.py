"""Render the synthetic backtest, declared experiment and two historical studies."""

import argparse
import math
from pathlib import Path

from demo_reports import record_walkthrough
from demo_style import (
    AMBER,
    BLUE,
    GRID,
    INK,
    MUTED,
    TEAL,
    base,
    chart,
    ease,
    encode,
    label,
    legend,
    metric,
    panel,
    preview,
    save_data,
    text,
)

DURATION = 86
CHAPTERS = [
    (0, "Price signal"),
    (9, "Timing"),
    (18, "Costs"),
    (28, "Experiment"),
    (43, "AAPL"),
    (58, "Industries"),
    (73, "Uncertainty"),
]


def dates(draw, left=200, right=1170):
    text(draw, (left, 702), "01 Feb 2024", 22, MUTED)
    text(draw, (right, 702), "22 Mar 2024", 22, MUTED, anchor="rt")


def experiment_frame(draw, data):
    grid = data["experiment"]
    params = grid["configuration"]["parameters"]
    results = {
        (row["lookback"], row["cost_bps"]): row["total_return"]
        for row in grid["comparison"]
        if row["model"] == "strategy"
    }
    panel(draw, (80, 250, 1130, 917))
    panel(draw, (1170, 250, 1840, 917))
    label(draw, 120, 290, "Net strategy return · synthetic development period", AMBER)
    text(draw, (125, 387), "Lookback", 28, MUTED)
    for j, cost in enumerate(params["cost_bps"]):
        text(draw, (590 + j * 239, 387), f"{cost} bps", 29, MUTED, anchor="rt")
    for i, lookback in enumerate(params["lookbacks"]):
        y = 490 + i * 102
        text(draw, (125, y), f"{lookback} closes", 32)
        for j, cost in enumerate(params["cost_bps"]):
            text(
                draw,
                (590 + j * 239, y),
                f"{results[lookback, cost]:+.2%}",
                34,
                TEAL,
                anchor="rt",
                mono=True,
            )
        draw.line((125, y + 61, 1084, y + 61), fill=GRID)
    text(draw, (125, 843), "10 basis points = 0.10% of the value traded.", 29, MUTED)
    label(draw, 1210, 290, "A declared experiment")
    metric(draw, 1210, 373, str(len(results)), "settings on the same dates", AMBER)
    text(draw, (1210, 533), "Lag 1 executes at the next close.", 28)
    text(draw, (1210, 601), "Each setting also runs buy-and-hold", 26)
    text(draw, (1210, 644), "and cash on the same intervals.", 26)
    text(draw, (1210, 765), "Checksums identify the CSV, JSON", 25, MUTED)
    text(draw, (1210, 810), "declaration, and implementation.", 25, MUTED)


def historical_frame(draw, study, *, monthly, progress):
    panel(draw, (80, 250, 1175, 917))
    panel(draw, (1215, 250, 1840, 917))
    label(draw, 120, 289, "Growth of 1.00 after trading costs")
    models = [
        ("strategy", "Momentum", TEAL),
        ("buy_and_hold", "Buy-and-hold", BLUE),
        ("cash", "Cash", AMBER),
    ]
    legend(
        draw, 190, 350, [(caption, colour) for _, caption, colour in models], gap=310
    )
    lines = [(caption, study["equity"][key], colour) for key, caption, colour in models]
    values = [v for _, series, _ in lines for v in series]
    tick = 0.5 if monthly else 0.05
    limits = (
        math.floor(min(values) / tick) * tick,
        math.ceil(max(values) / tick) * tick,
    )
    chart(draw, (215, 430, 1120, 720), lines, limits, progress=progress)
    text(draw, (215, 746), study["start"], 24, MUTED)
    text(draw, (1120, 746), study["end"], 24, MUTED, anchor="rt")
    text(
        draw,
        (120, 842),
        "Cash earns the archive’s monthly cash rate."
        if monthly
        else "The daily pilot assumes zero return on cash.",
        27,
        MUTED,
    )
    label(draw, 1255, 289, "Fixed evaluation rule", AMBER)
    unit = "months" if monthly else "closes"
    text(
        draw,
        (1255, 370),
        f"Lookback {study['lookback']} {unit} · {study['cost_bps']} bps",
        28,
    )
    text(draw, (1255, 430), "Orders execute one observation later.", 25, MUTED)
    for x, caption in [(1600, "Momentum"), (1798, "Buy & hold")]:
        text(draw, (x, 539), caption, 24, MUTED, anchor="rt")
    first = (
        ("Annualised", "annualised_return")
        if monthly
        else ("Total return", "total_return")
    )
    for i, (caption, key) in enumerate([first, ("Drawdown", "max_drawdown")]):
        y = 612 + i * 85
        text(draw, (1255, y), caption, 27)
        for x, model, colour in [
            (1600, "strategy", TEAL),
            (1798, "buy_and_hold", BLUE),
        ]:
            text(
                draw,
                (x, y),
                f"{study['metrics'][model][key]:.2%}",
                29,
                colour,
                mono=True,
                anchor="rt",
            )
    text(draw, (1255, 823), "Drawdown is the largest fall", 24, MUTED)
    text(draw, (1255, 858), "from an earlier peak.", 24, MUTED)


def uncertainty_frame(draw, data):
    rows = data["studies"]["industry"]["uncertainty"]
    panel(draw, (80, 250, 1155, 917))
    panel(draw, (1195, 250, 1840, 917))
    label(draw, 120, 289, "Industry study · 95% intervals for the mean difference")
    text(draw, (120, 370), "Momentum minus buy-and-hold, annualised", 29)
    limits = max(abs(bound) for row in rows for bound in row["percentile_95"]) * 1.08

    def x(value):
        return 670 + value / limits * 410

    draw.line((x(0), 460, x(0), 777), fill=AMBER, width=3)
    text(draw, (x(0), 419), "0%", 24, AMBER, anchor="mt")
    for i, row in enumerate(rows):
        y = 510 + i * 108
        lo, hi = row["percentile_95"]
        dot = x(row["estimate"])
        text(draw, (120, y - 15), f"{row['block_size']} months", 25, MUTED)
        draw.line((x(lo), y, x(hi), y), fill=TEAL, width=6)
        for end, value in [(x(lo), lo), (x(hi), hi)]:
            draw.line((end, y - 10, end, y + 10), fill=TEAL, width=3)
            text(draw, (end, y + 23), f"{value:+.2%}", 23, MUTED, anchor="mt")
        draw.ellipse((dot - 8, y - 8, dot + 8, y + 8), fill=INK)
    text(
        draw,
        (120, 845),
        "Each row uses a different block length when resampling months.",
        25,
        MUTED,
    )
    label(draw, 1235, 289, "What the sample can tell us", AMBER)
    crossing = sum(r["percentile_95"][0] <= 0 <= r["percentile_95"][1] for r in rows)
    metric(
        draw, 1235, 365, f"{crossing} / {len(rows)}", "intervals include zero", AMBER
    )
    text(draw, (1235, 532), "The mean difference is uncertain.", 27)
    text(draw, (1235, 598), "Both histories were studied", 26, MUTED)
    text(draw, (1235, 642), "retrospectively.", 26, MUTED)
    text(draw, (1235, 751), "Read the full metrics and limitations", 26)
    text(draw, (1235, 797), "in research/results/.", 26)


def frame(t, data):
    run = data["runs"]["lb5_cost10"]
    stats = run["strategy"]["metrics"]
    section = max(i for i, (start, _) in enumerate(CHAPTERS) if t >= start)
    titles = [
        "From a price history to a position.",
        "A signal can only act on the next interval.",
        "Compound returns. Charge the trades.",
        "Declare the settings before you run them.",
        "How did momentum fare on AAPL in 2016?",
        "Repeat the test across 12 industry portfolios.",
        "How uncertain is the return difference?",
    ]
    image, draw = base(
        "quant-research",
        3,
        titles[section],
        [
            "Synthetic prices  /  the rule holds the asset when its price rises over five observations.",
            "Synthetic prices  /  the default example trades at the close that generated the signal (lag 0).",
            "Synthetic prices  /  compare a fixed rule, buy-and-hold, and cash over the same dates.",
            "uv run quant-research --experiment examples/synthetic_experiment.json",
            "Historical daily pilot  /  2015 supplies warm-up prices for the fixed 2016 evaluation.",
            "Historical monthly study  /  1980–1999 development  /  2000–2016 evaluation",
            "Paired block resampling keeps nearby strategy and benchmark returns together.",
        ][section],
        CHAPTERS,
        t,
        DURATION,
        AMBER,
        (
            "Bundled synthetic prices illustrate portfolio accounting. All three models start in cash and keep their final positions."
            if section < 4
            else "Historical results use archived data and idealised execution. The studies use different assets and time intervals."
        ),
    )
    if section == 0:
        panel(draw, (80, 250, 1250, 917))
        label(draw, 120, 285, "Adjusted-close input · 60 weekday observations")
        x0, x1 = 210, 1200
        split = x0 + run["history_observations"] / (len(data["prices"]) - 1) * (x1 - x0)
        draw.rectangle((x0, 370, split, 690), fill="#18273b")
        progress = 0.25 + 0.75 * ease(t / 4)
        chart(
            draw,
            (x0, 370, x1, 690),
            [("Price", data["prices"], BLUE)],
            (96, 108),
            progress=progress,
        )
        draw.line((split, 350, split, 785), fill=AMBER, width=2)
        text(draw, (x0, 325), "History only", 23, MUTED)
        text(draw, (split + 20, 325), "Evaluation starts 01 Feb", 23, AMBER)
        for i, position in enumerate(data["signals"][:-1]):
            left = x0 + i / 59 * (x1 - x0)
            right = x0 + (i + 1) / 59 * (x1 - x0)
            if (i + 1) / 59 <= progress:
                draw.rectangle((left, 750, right, 781), fill=TEAL if position else GRID)
        text(draw, (x0, 710), "01 Jan", 21, MUTED)
        text(draw, (x1, 710), "22 Mar", 21, MUTED, anchor="rt")
        legend(
            draw,
            210,
            815,
            [("Long next interval", TEAL), ("Cash next interval", GRID)],
            gap=420,
        )
        text(
            draw,
            (120, 870),
            "Every position uses only the history available at that close.",
            24,
            MUTED,
        )
        panel(draw, (1290, 250, 1840, 917))
        label(draw, 1330, 290, "Fixed momentum rule")
        text(draw, (1330, 355), "P[t] > P[t − 5]", 34, TEAL, mono=True)
        text(draw, (1330, 420), "true → 100% long", 30)
        text(draw, (1330, 473), "false → cash", 30, MUTED)
        metric(
            draw,
            1330,
            560,
            str(stats["observations"]),
            "evaluation return intervals",
            AMBER,
        )
        text(draw, (1330, 730), "5-observation lookback", 26)
        text(draw, (1330, 775), "10 bps proportional costs", 26)
        text(draw, (1330, 845), "The settings are fixed in advance.", 23, MUTED)
    elif section == 1:
        event = data["dates"].index("2024-02-07")
        old, latest, following = (
            data["prices"][event - 5],
            data["prices"][event],
            data["prices"][event + 1],
        )
        weight = data["signals"][event]
        interval = event - run["history_observations"]
        earned = run["strategy"]["path"]["returns"][interval]
        cost = run["strategy"]["path"]["costs"][interval]
        asset_return = data["asset_returns"][event]
        label(draw, 80, 260, "One actual signal boundary from the recorded path")
        for x, caption, value, detail, colour in [
            (80, "31 JAN / t − 5", old, "Historical close", BLUE),
            (690, "07 FEB / t", latest, "Signal becomes CASH", TEAL),
            (1300, "08 FEB / t + 1", following, "Next observed close", AMBER),
        ]:
            panel(draw, (x, 325, x + 540, 615))
            label(draw, x + 35, 365, caption, colour)
            metric(draw, x + 35, 425, f"{value:.4f}", detail, colour, size=44)
        text(draw, (639, 450), "→", 42, MUTED)
        text(draw, (1250, 450), "→", 42, MUTED)
        panel(draw, (80, 655, 990, 917))
        label(draw, 120, 690, "At t · compare only known prices")
        text(draw, (120, 743), f"{latest:.4f} < {old:.4f}", 36, TEAL, mono=True)
        text(
            draw,
            (120, 807),
            f"Target weight = {weight:.0f}. Exit the long position.",
            29,
        )
        text(
            draw,
            (120, 859),
            "The price change ending at t cannot be earned by this signal.",
            23,
            MUTED,
        )
        panel(draw, (1030, 655, 1840, 917))
        label(draw, 1070, 690, "Following interval · t to t + 1")
        text(
            draw,
            (1070, 748),
            f"Asset return   {asset_return:+.3%}",
            31,
            AMBER,
            mono=True,
        )
        text(draw, (1070, 808), f"Strategy net   {earned:+.3%}", 31, TEAL, mono=True)
        text(
            draw,
            (1070, 866),
            f"Cash earns zero. The exit costs {cost:.3%}.",
            25,
            MUTED,
        )
    elif section == 2:
        panel(draw, (80, 250, 1250, 917))
        label(draw, 120, 285, "Equity from 1.00 · same evaluation horizon")
        legend(
            draw,
            210,
            335,
            [("Momentum / 10 bps", TEAL), ("Buy & hold / 10 bps", BLUE)],
            gap=470,
        )
        chart(
            draw,
            (210, 405, 1200, 690),
            [
                ("Strategy", run["strategy"]["equity"], TEAL),
                ("Benchmark", run["buy_and_hold"]["equity"], BLUE),
            ],
            (0.94, 1.06),
            progress=0.15 + 0.85 * ease((t - 18) / 5),
        )
        dates(draw, 210, 1200)
        label(draw, 120, 762, "Position / turnover / fee are recorded per interval")
        text(
            draw,
            (120, 810),
            "net return = (1 − fee) × (1 + weight × asset return) − 1",
            25,
            TEAL,
            mono=True,
        )
        text(
            draw,
            (120, 868),
            "Both paths start flat and pay their applicable initial entry cost.",
            25,
            MUTED,
        )
        panel(draw, (1290, 250, 1840, 917))
        label(draw, 1330, 290, "Completed synthetic run")
        metric(
            draw,
            1330,
            345,
            f"{stats['total_return']:+.2%}",
            "strategy total return",
            TEAL,
        )
        rows = [
            ("Buy & hold", f"{run['buy_and_hold']['metrics']['total_return']:+.2%}"),
            ("Max drawdown", f"{stats['max_drawdown']:.2%}"),
            ("Ann. volatility", f"{stats['annualised_volatility']:.2%}"),
            ("Sharpe / zero rf", f"{stats['sharpe_zero_rf']:.2f}"),
            ("Total turnover", f"{run['strategy']['total_turnover']:.3f}×"),
        ]
        for i, (caption, value) in enumerate(rows):
            y = 510 + i * 63
            text(draw, (1330, y), caption, 23, MUTED)
            text(draw, (1800, y), value, 27, INK, mono=True, anchor="rt")
        text(draw, (1330, 855), "252 periods/year · 36 intervals.", 23, MUTED)
    elif section == 3:
        experiment_frame(draw, data)
    elif section in (4, 5):
        monthly = section == 5
        study = data["studies"]["industry" if monthly else "apple"]
        historical_frame(
            draw,
            study,
            monthly=monthly,
            progress=0.12 + 0.88 * ease((t - CHAPTERS[section][0]) / 5),
        )
    else:
        uncertainty_frame(draw, data)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/media"))
    parser.add_argument("--stills-only", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = record_walkthrough(Path(__file__).resolve().parents[1])
    save_data(args.output_dir / "demo-data.json", data)
    if args.stills_only:
        for start, _ in CHAPTERS:
            t = start + 5
            frame(t, data).save(args.output_dir / f"frame-{t}.png")
        return
    encode(lambda t: frame(t, data), args.output_dir / "demo.mp4", DURATION, CHAPTERS)
    preview(
        args.output_dir / "demo.mp4", args.output_dir / "preview.gif", CHAPTERS[5][0], 8
    )


if __name__ == "__main__":
    main()
