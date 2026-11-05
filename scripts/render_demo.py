"""Render the synthetic CLI backtest, signal timing, and declared sensitivities."""

import argparse
from pathlib import Path

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

from quant_research.demo_data import build_demo

DURATION = 38
CHAPTERS = [
    (0, "Observe prices"),
    (9, "Respect chronology"),
    (18, "Account for costs"),
    (28, "Inspect sensitivity"),
]


def dates(draw, left=200, right=1170):
    text(draw, (left, 702), "01 Feb 2024", 22, MUTED)
    text(draw, (right, 702), "22 Mar 2024", 22, MUTED, anchor="rt")


def frame(t, data):
    run = data["runs"]["lb5_cost10"]
    stats = run["strategy"]["metrics"]
    section = 0 if t < 9 else 1 if t < 18 else 2 if t < 28 else 3
    titles = [
        "From a price history to a position.",
        "A signal can only act on the next interval.",
        "Compound returns. Charge the trades.",
        "Change assumptions. Show every result.",
    ]
    image, draw = base(
        "quant-research",
        3,
        titles[section],
        "SYNTHETIC DATA  /  single asset  /  reproducible, descriptive research",
        CHAPTERS,
        t,
        DURATION,
        AMBER,
        "Synthetic demonstration, not investment performance. Idealised close fills; zero cash/risk-free return; no final liquidation.",
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
        text(draw, (1330, 845), "Parameters are fixed, not fitted.", 23, MUTED)
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
            f"Cash earns zero; exiting still costs {cost:.3%}.",
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
        text(draw, (1330, 855), "252 periods/year; 36 intervals.", 23, MUTED)
    else:
        panel(draw, (80, 250, 1180, 917))
        label(draw, 120, 290, "Same 5-observation signal · different costs")
        legend(
            draw,
            210,
            345,
            [("0 bps", TEAL), ("10 bps", BLUE), ("50 bps", AMBER)],
            gap=260,
        )
        series = [
            (str(cost), data["runs"][f"lb5_cost{cost}"]["strategy"]["equity"], colour)
            for cost, colour in [(0, TEAL), (10, BLUE), (50, AMBER)]
        ]
        chart(
            draw,
            (210, 415, 1120, 690),
            series,
            (0.97, 1.06),
            progress=0.15 + 0.85 * ease((t - 28) / 3),
        )
        dates(draw, 210, 1120)
        for i, (cost, colour) in enumerate([(0, TEAL), (10, BLUE), (50, AMBER)]):
            x = 120 + 345 * i
            result = data["runs"][f"lb5_cost{cost}"]["strategy"]["metrics"]
            metric(
                draw,
                x,
                780,
                f"{result['total_return']:+.2%}",
                f"total return / {cost} bps",
                colour,
                size=36,
            )
        panel(draw, (1220, 250, 1840, 917))
        label(draw, 1260, 290, "Lookback sensitivity · 10 bps")
        text(draw, (1260, 355), "Lookback", 24, MUTED)
        text(draw, (1800, 355), "Total return", 24, MUTED, anchor="rt")
        for i, lookback in enumerate([3, 5, 10]):
            result = data["runs"][f"lb{lookback}_cost10"]["strategy"]["metrics"]
            y = 430 + i * 85
            text(draw, (1260, y), f"{lookback} observations", 28)
            text(
                draw,
                (1800, y),
                f"{result['total_return']:+.2%}",
                31,
                AMBER,
                mono=True,
                anchor="rt",
            )
            draw.line((1260, y + 50, 1800, y + 50), fill=GRID)
        text(draw, (1260, 715), "All declared variants shown.", 27, AMBER)
        text(draw, (1260, 763), "No fitting. No profitability inference.", 24, MUTED)
        text(draw, (1260, 825), "CSV hash + settings + full paths", 24)
        text(draw, (1260, 866), "saved in demo-data.json", 24, TEAL, mono=True)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/media"))
    parser.add_argument("--stills-only", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = build_demo(
        Path(__file__).resolve().parents[1] / "examples/synthetic_prices.csv"
    )
    save_data(args.output_dir / "demo-data.json", data)
    if args.stills_only:
        for t in (5, 13, 24, 34):
            frame(t, data).save(args.output_dir / f"frame-{t}.png")
        return
    encode(lambda t: frame(t, data), args.output_dir / "demo.mp4", DURATION)
    preview(args.output_dir / "demo.mp4", args.output_dir / "demo.gif", 0, DURATION)


if __name__ == "__main__":
    main()
