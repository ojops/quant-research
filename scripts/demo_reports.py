"""Assemble film data from the synthetic CLI, declared experiment and saved studies."""

import hashlib
import json
from pathlib import Path

from check_report_provenance import check_reports

from quant_research.analysis import equity_curve
from quant_research.demo_data import build_demo
from quant_research.experiment import run_experiment


def record_walkthrough(root: Path) -> dict:
    errors = check_reports(root)
    if errors:
        raise ValueError("\n".join(errors))

    data = build_demo(root / "examples/synthetic_prices.csv")
    grid = run_experiment(root / "examples/synthetic_experiment.json")
    data["experiment"] = {
        key: grid[key]
        for key in (
            "configuration",
            "configuration_sha256",
            "input_sha256",
            "comparison",
        )
    }
    studies = {}
    for name in ("apple", "industry"):
        path = root / f"research/results/{name}-momentum.json"
        raw = path.read_bytes()
        report = json.loads(raw)
        result = report["fixed_evaluation"]
        if name == "apple":
            paths = report["fixed_evaluation_path"]
            models = ("strategy", "buy_and_hold", "cash")
            metrics = {model: result[model]["metrics"] for model in models}
            returns = {model: paths[model]["returns"] for model in models}
            lookback = result["lookback"]
        else:
            metrics, returns = result["aggregate"], result["aggregate_returns"]
            lookback = result["lookback_months"]
        studies[name] = {
            "file": str(path.relative_to(root)),
            "report_sha256": hashlib.sha256(raw).hexdigest(),
            "data_sha256": report["source"]["sha256"],
            "start": result["start"],
            "end": result["end"],
            "cost_bps": result["cost_bps"],
            "lookback": lookback,
            "metrics": metrics,
            "uncertainty": report["uncertainty"],
            "equity": {
                model: equity_curve(values) for model, values in returns.items()
            },
        }
    data["studies"] = studies
    return data
