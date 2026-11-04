"""Capture actual CLI reports and signal history for a synthetic research film."""

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from quant_research.analysis import equity_curve, simple_returns
from quant_research.backtest import momentum_weights
from quant_research.data import load_prices
from quant_research.main import main


def build_demo(csv_path: Path) -> dict:
    """Run every declared sensitivity through the production CLI on one horizon."""
    series = load_prices(csv_path)
    runs = {}
    for lookback, cost in ((5, 0), (5, 10), (5, 50), (3, 10), (10, 10)):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = main(
                [
                    str(csv_path),
                    "--test-start",
                    "2024-02-01",
                    "--lookback",
                    str(lookback),
                    "--cost-bps",
                    str(cost),
                ]
            )
        if code != 0:
            raise RuntimeError("Backtest CLI failed")
        report = json.loads(stream.getvalue())
        for key in ("strategy", "buy_and_hold"):
            report[key]["equity"] = equity_curve(report[key]["path"]["returns"])
        runs[f"lb{lookback}_cost{cost}"] = report
    return {
        "dataset": "Bundled deterministic synthetic prices, not market data",
        "dates": [str(day) for day in series.dates],
        "prices": series.prices,
        "asset_returns": simple_returns(series.prices),
        "signals": momentum_weights(series.prices, lookback=5),
        "runs": runs,
        "note": "Fixed illustrative sensitivities, no fitting or evidence of profitability.",
    }
