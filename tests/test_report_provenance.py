"""Saved evidence must identify the code currently supplied with the project."""

import hashlib
import json
import runpy
from pathlib import Path

import pytest

check_reports = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/check_report_provenance.py")
)["check_reports"]


@pytest.fixture
def saved_studies(tmp_path):
    source = tmp_path / "src/quant_research"
    source.mkdir(parents=True)
    module = source / "study.py"
    module.write_text("original implementation\n")
    results = tmp_path / "research/results"
    results.mkdir(parents=True)
    for name in ("apple-momentum.json", "industry-momentum.json"):
        (results / name).write_text(
            json.dumps(
                {
                    "implementation_sha256": {
                        "study.py": hashlib.sha256(module.read_bytes()).hexdigest()
                    }
                }
            )
        )
    return tmp_path


def test_current_reports_pass_then_changed_code_is_reported(saved_studies):
    assert check_reports(saved_studies) == []
    (saved_studies / "src/quant_research/study.py").write_text("changed\n")
    errors = check_reports(saved_studies)
    assert len(errors) == 2
    assert all("study.py" in error for error in errors)


@pytest.mark.parametrize("change", ["add", "remove", "corrupt", "missing"])
def test_added_removed_sources_and_unreadable_reports_fail(saved_studies, change):
    source = saved_studies / "src/quant_research"
    report = saved_studies / "research/results/apple-momentum.json"
    if change == "add":
        (source / "new.py").write_text("new module\n")
    elif change == "remove":
        (source / "study.py").unlink()
    elif change == "corrupt":
        report.write_text("not JSON")
    else:
        report.unlink()
    assert check_reports(saved_studies)
