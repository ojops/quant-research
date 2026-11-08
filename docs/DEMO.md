# Portfolio video: reproduction and verification

The README embeds an **eight-second looping GIF** (`docs/media/preview.gif`) linked to a complete **38-second, silent 1080p MP4** (`docs/media/demo.mp4`).

The media shows results from the existing **synthetic** price example. It retains the original signal-close execution (`execution_lag=0`); the new declared experiment uses lag 1 and does not replace this recording. It does not depict live trading or demonstrate a profitable strategy.

## Generate

From the repository root, with Python 3.10 and [uv](https://docs.astral.sh/uv/):

```bash
uv sync --locked --extra demo
uv run --locked --extra demo python scripts/render_demo.py
```

Install FFmpeg with H.264 support and DejaVu fonts (Ubuntu: `ffmpeg`, `fonts-dejavu-core`). Pillow is installed through the optional `demo` extra. Rendering uses the CPU, without a market-data connection or graphical display.

Use `--output-dir /path/to/output` for another destination. To inspect four chapter layouts without video encoding:

```bash
uv run --locked --extra demo python scripts/render_demo.py --stills-only --output-dir /tmp/quant-demo-stills
```

## What the film demonstrates

| Time | Content |
| --- | --- |
| 0–9 s | Synthetic prices, evaluation start and next-interval positions |
| 9–18 s | A cash signal, its next return interval and the exit fee |
| 18–28 s | Net strategy vs buy-and-hold wealth and risk metrics |
| 28–38 s | Fixed sensitivity checks for costs and lookback periods |

`quant_research.demo_data.build_demo()` runs the existing CLI with the bundled `examples/synthetic_prices.csv` (60 weekday observations, 2024-01-01 to 2024-03-22). The evaluation uses 36 intervals beginning 2024-02-01. The generator records the CLI settings and paths, and derives chart data from the existing analysis functions rather than inventing results.

The demonstration compares these **preselected settings**:

| Lookback | Cost (bps) | Recorded total return (synthetic) |
| --- | --- | --- |
| 5 | 0 | +5.72% |
| 5 | 10 | +5.20% |
| 5 | 50 | +3.11% |
| 3 | 10 | +8.61% |
| 10 | 10 | −2.66% |

These figures describe the committed recording, not forecasts or evidence of generalisable performance. The complete paths and input checksum are stored in `docs/media/demo-data.json`.

**Signal timing:** A 7 February cash signal applies to the subsequent return interval. The example records a −0.908% asset return and a −0.100% strategy return from the exit fee. The strategy does not capture the move that generated the signal.

The model assumes idealised close fills, proportional costs, a zero-return cash position and no final liquidation. With only 36 intervals, annualised volatility and zero-risk-free Sharpe are descriptive, not statistically validated estimates. See [research methods](RESEARCH.md).

## Validate

```bash
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
ffmpeg -v error -i docs/media/demo.mp4 -f null -
ffmpeg -v error -i docs/media/preview.gif -f null -
```

Tests compare the recorded CLI paths and metrics, timing, costs, evaluation horizons and deterministic output. Encoded media bytes can vary with FFmpeg and font versions.

**When updating the media:** regenerate and commit the MP4, GIF and JSON together. The README's MP4 URL is pinned to a media commit and needs updating whenever the video changes.
