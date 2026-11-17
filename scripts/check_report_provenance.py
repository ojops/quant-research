"""Check saved study source hashes offline; this does not rerun the research."""

import hashlib
import json
from pathlib import Path

REPORTS = ("apple-momentum.json", "industry-momentum.json")


def check_reports(root: Path) -> list[str]:
    current = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((root / "src/quant_research").glob("*.py"))
    }
    if not current:
        return ["No implementation files found"]
    errors = []
    for name in REPORTS:
        path = root / "research/results" / name
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(report, dict):
                raise ValueError("Expected a JSON object")
            recorded = report.get("implementation_sha256")
            if not isinstance(recorded, dict):
                raise ValueError("Missing implementation_sha256 mapping")
        except (OSError, ValueError) as error:
            errors.append(f"{name}: {error}")
            continue
        for module in sorted(current.keys() | recorded.keys()):
            if (
                module not in current
                or module not in recorded
                or current[module] != recorded[module]
            ):
                errors.append(f"{name}: stale or missing source hash for {module}")
    return errors


def main() -> int:
    errors = check_reports(Path(__file__).resolve().parents[1])
    if errors:
        print("\n".join(errors))
        print(
            "Regenerate both studies and review the differences; see docs/RESEARCH.md."
        )
        return 1
    print("Both saved studies match the current implementation hashes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
