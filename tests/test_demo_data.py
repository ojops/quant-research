"""Check the presentation's horizon, causal interval and complete sensitivities."""

import json
from pathlib import Path

import pytest

from quant_research.demo_data import build_demo
from quant_research.main import main

CSV = Path(__file__).resolve().parents[1] / "examples/synthetic_prices.csv"


def test_recording_preserves_the_actual_cli_report(capsys):
    report = build_demo(CSV)
    assert main([str(CSV), "--test-start", "2024-02-01"]) == 0
    cli = json.loads(capsys.readouterr().out)
    recorded = report["runs"]["lb5_cost10"]
    for name in ("strategy", "buy_and_hold"):
        assert recorded[name]["path"] == cli[name]["path"]
        assert recorded[name]["metrics"] == cli[name]["metrics"]
        assert recorded[name]["equity"][-1] == pytest.approx(
            1 + cli[name]["metrics"]["total_return"]
        )
    assert recorded["input_sha256"] == cli["input_sha256"]


def test_signal_boundary_exits_before_the_next_return_and_pays_fee():
    report = build_demo(CSV)
    event = report["dates"].index("2024-02-07")
    run = report["runs"]["lb5_cost10"]
    interval = event - run["history_observations"]
    path = run["strategy"]["path"]
    assert report["signals"][event - 1 : event + 1] == (1.0, 0.0)
    assert path["positions"][interval] == 0
    assert path["returns"][interval] == pytest.approx(-0.001)
    assert path["costs"][interval] == pytest.approx(0.001)


def test_all_declared_variants_keep_one_horizon_and_costs_reduce_wealth():
    report = build_demo(CSV)
    assert set(report["runs"]) == {
        "lb5_cost0",
        "lb5_cost10",
        "lb5_cost50",
        "lb3_cost10",
        "lb10_cost10",
    }
    for run in report["runs"].values():
        assert run["test_start"] == "2024-02-01"
        assert run["strategy"]["metrics"]["observations"] == 36
    wealth = [
        report["runs"][f"lb5_cost{cost}"]["strategy"]["equity"][-1]
        for cost in (0, 10, 50)
    ]
    assert wealth[0] > wealth[1] > wealth[2]
    assert build_demo(CSV) == report
