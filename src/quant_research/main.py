"""Compare fixed rules or reproduce a declared research experiment."""

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

from quant_research.data import parse_prices
from quant_research.evaluation import evaluate
from quant_research.experiment import run_experiment


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, nargs="?")
    parser.add_argument(
        "--experiment", type=Path, help="Checksum-pinned experiment JSON"
    )
    parser.add_argument(
        "--test-start",
        type=date.fromisoformat,
        help="First evaluation valuation date (must occur in the CSV)",
    )
    parser.add_argument("--test-end", type=date.fromisoformat)
    parser.add_argument("--lookback", type=int)
    parser.add_argument("--cost-bps", type=float)
    parser.add_argument("--periods-per-year", type=int)
    parser.add_argument(
        "--execution-lag",
        type=int,
        choices=(0, 1),
        help="0: idealised signal-close fill (default); 1: next-close fill",
    )
    args = parser.parse_args(argv)

    try:
        overrides = (
            args.test_start,
            args.test_end,
            args.lookback,
            args.cost_bps,
            args.periods_per_year,
            args.execution_lag,
        )
        if args.experiment:
            if args.csv is not None or any(value is not None for value in overrides):
                raise ValueError(
                    "--experiment cannot be combined with CSV or parameter overrides"
                )
            output = run_experiment(args.experiment)
        else:
            if args.csv is None or args.test_start is None:
                raise ValueError("Provide a CSV and --test-start, or --experiment")
            snapshot = args.csv.read_bytes()
            output = evaluate(
                parse_prices(snapshot.decode("utf-8")),
                args.test_start,
                end=args.test_end,
                lookback=args.lookback if args.lookback is not None else 5,
                cost_bps=args.cost_bps if args.cost_bps is not None else 10,
                periods_per_year=args.periods_per_year
                if args.periods_per_year is not None
                else 252,
                execution_lag=args.execution_lag
                if args.execution_lag is not None
                else 0,
            )
            output = {"input_sha256": hashlib.sha256(snapshot).hexdigest(), **output}
        print(json.dumps(output, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
