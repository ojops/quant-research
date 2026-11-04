"""Compare a fixed momentum rule and buy and hold on a chronological holdout"""

import argparse
import hashlib
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from quant_research.analysis import performance
from quant_research.backtest import momentum_weights, run_backtest
from quant_research.data import load_prices


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument(
        "--test-start",
        required=True,
        type=date.fromisoformat,
        help="First holdout valuation date (must occur in the CSV)",
    )
    parser.add_argument("--lookback", type=int, default=5)
    parser.add_argument("--cost-bps", type=float, default=10)
    parser.add_argument("--periods-per-year", type=int, default=252)
    args = parser.parse_args(argv)

    try:
        series = load_prices(args.csv)
        index = series.dates.index(args.test_start)
        if index < args.lookback or len(series.prices) - index < 3:
            raise ValueError(
                "Holdout needs prior lookback history and at least three prices"
            )

        targets = momentum_weights(series.prices, args.lookback)[index:]
        prices = series.prices[index:]
        strategy = run_backtest(prices, targets, args.cost_bps)
        benchmark = run_backtest(prices, [1.0] * len(prices), args.cost_bps)

        def report(result):
            return {
                "metrics": performance(result.returns, args.periods_per_year),
                "total_turnover": sum(result.turnover),
                "path": asdict(result),
            }

        output = {
            "input_sha256": hashlib.sha256(args.csv.read_bytes()).hexdigest(),
            "settings": {
                "lookback": args.lookback,
                "cost_bps": args.cost_bps,
                "periods_per_year": args.periods_per_year,
            },
            "history_observations": index,
            "test_start": str(series.dates[index]),
            "test_end": str(series.dates[-1]),
            "assumptions": "Single asset, adjusted prices, zero cash/risk free rate, close execution, and no final liquidation",
            "strategy": report(strategy),
            "buy_and_hold": report(benchmark),
        }
        print(json.dumps(output, indent=2, allow_nan=False))

        return 0
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
