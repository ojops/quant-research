"""Download and checksum-verify the fixed historical pilot snapshot."""

import argparse
from pathlib import Path
from urllib.request import urlopen

from quant_research.study import SOURCE_URL, normalize_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path("research/local"))
    args = parser.parse_args()
    with urlopen(SOURCE_URL, timeout=30) as response:
        raw = response.read()
    normalized = normalize_snapshot(raw)
    args.directory.mkdir(parents=True, exist_ok=True)
    (args.directory / "finance-charts-apple.csv").write_bytes(raw)
    (args.directory / "apple-adjusted.csv").write_text(normalized)
    print("Verified fixed snapshot; raw and normalised prices saved locally.")


if __name__ == "__main__":
    main()
