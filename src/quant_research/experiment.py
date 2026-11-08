"""Load predeclared experiments and retain every fixed sensitivity result."""

import hashlib
import json
import platform
from datetime import date
from itertools import product
from pathlib import Path

from quant_research.data import parse_prices
from quant_research.evaluation import evaluate


def _object(value, required, label):
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError(f"{label} must contain exactly: {', '.join(required)}")
    return value


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate experiment key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"Non-finite experiment number: {value}")


def run_experiment(path: Path) -> dict:
    """Run a checksum-pinned JSON experiment; resolve data relative to its file.

    Development runs retain the entire Cartesian sensitivity grid. A declared
    holdout accepts one fixed setting only; the software cannot certify that
    its observations have never previously been inspected.
    """
    raw_config = path.read_bytes()
    config = _object(
        json.loads(
            raw_config,
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        ),
        ("schema_version", "name", "hypothesis", "data", "evaluation", "parameters"),
        "experiment",
    )
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    for key in ("name", "hypothesis"):
        if not isinstance(config[key], str) or not config[key].strip():
            raise ValueError(f"{key} must be nonempty text")
    data = _object(config["data"], ("path", "sha256", "provenance"), "data")
    provenance = _object(
        data["provenance"],
        ("kind", "source", "licence", "adjustments", "retrieved_at", "limitations"),
        "provenance",
    )
    if any(not isinstance(v, str) or not v.strip() for v in provenance.values()):
        raise ValueError("Every provenance field must be nonempty text")
    if provenance["kind"] not in ("synthetic", "market"):
        raise ValueError("provenance.kind must be synthetic or market")
    evaluation = _object(config["evaluation"], ("start", "end", "role"), "evaluation")
    if evaluation["role"] not in ("development", "declared_holdout"):
        raise ValueError("evaluation.role must be development or declared_holdout")
    start, end = (date.fromisoformat(evaluation[key]) for key in ("start", "end"))
    parameters = _object(
        config["parameters"],
        ("lookbacks", "cost_bps", "periods_per_year", "execution_lag"),
        "parameters",
    )
    for key in ("lookbacks", "cost_bps"):
        values = parameters[key]
        if not isinstance(values, list) or not values:
            raise ValueError(f"{key} must be a nonempty list")
        if any(value in values[:i] for i, value in enumerate(values)):
            raise ValueError(f"{key} must not contain duplicates")
    if evaluation["role"] == "declared_holdout" and (
        len(parameters["lookbacks"]) != 1 or len(parameters["cost_bps"]) != 1
    ):
        raise ValueError(
            "Declared holdouts require one lookback and one cost; use development for sensitivity"
        )
    if not isinstance(data["path"], str) or not data["path"]:
        raise ValueError("data.path must be a nonempty path")
    snapshot = (path.parent / data["path"]).read_bytes()
    checksum = hashlib.sha256(snapshot).hexdigest()
    if data["sha256"] != checksum:
        raise ValueError(
            "Input SHA-256 mismatch; use the declared immutable data snapshot"
        )
    series = parse_prices(snapshot.decode("utf-8"))
    runs = [
        evaluate(
            series,
            start,
            end=end,
            lookback=lookback,
            cost_bps=cost,
            periods_per_year=parameters["periods_per_year"],
            execution_lag=parameters["execution_lag"],
        )
        for lookback, cost in product(parameters["lookbacks"], parameters["cost_bps"])
    ]
    comparisons = [
        {
            "run": index,
            "model": model,
            **run["settings"],
            **run[model]["metrics"],
            "total_turnover": run[model]["total_turnover"],
        }
        for index, run in enumerate(runs)
        for model in ("strategy", "buy_and_hold", "cash")
    ]
    return {
        "schema_version": 1,
        "configuration": config,
        "configuration_sha256": hashlib.sha256(raw_config).hexdigest(),
        "input_sha256": checksum,
        "implementation_sha256": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in sorted(Path(__file__).parent.glob("*.py"))
        },
        "python_version": platform.python_version(),
        "research_notice": "All variants are reported without ranking or selection. "
        "A declared holdout is a user assertion, not verified independence. "
        "Synthetic results demonstrate accounting, not investment performance.",
        "runs": runs,
        "comparison": comparisons,
    }
