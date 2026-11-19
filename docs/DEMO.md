# Portfolio video: reproduction and verification

The eight-second README preview traces the monthly industry study. The 1 minute 26 second silent MP4 starts with synthetic prices, runs the declared experiment, and then examines two historical studies. The MP4 includes chapter markers. The table below is a text companion.

## Generate

From the repository root, use Python 3.10, uv, FFmpeg with H.264 support, and DejaVu fonts. On Ubuntu the system packages are `ffmpeg` and `fonts-dejavu-core`. The optional `demo` extra supplies Pillow.

```bash
uv sync --locked --extra demo
uv run --locked --extra demo python scripts/render_demo.py
```

The renderer writes `demo.mp4`, `preview.gif`, and `demo-data.json` in `docs/media/`. It uses the bundled CSV and the checked-in research reports, so it runs offline after installation. To inspect a still from each chapter, run

```bash
uv run --locked --extra demo python scripts/render_demo.py --stills-only --output-dir /tmp/quant-demo-stills
```

## What the film demonstrates

| Time | Follow the example |
| --- | --- |
| 0:00–0:09 | **Price signal.** The bundled CSV contains 60 synthetic closes. A five-observation rule holds the asset when today’s price exceeds its earlier price. Otherwise the position is cash. The shaded observations supply history before evaluation begins. |
| 0:09–0:18 | **Timing.** On 7 February the signal turns to cash. With signal-close execution (lag 0), the next asset return is −0.908%. The strategy earns −0.100% from the fee on its exit. |
| 0:18–0:28 | **Costs.** Starting from 1.00 and charging 10 basis points on turnover gives +5.20% total return for the rule and +0.94% for buy-and-hold on this synthetic path. Cash earns zero. |
| 0:28–0:43 | **Declared experiment.** The JSON file fixes the data checksum, development dates, three lookbacks, and three costs. It delays execution to the next close (lag 1). At five observations and 10 bps, the same dates now give +1.28%. All nine settings are reported alongside both benchmarks. |
| 0:43–0:58 | **AAPL pilot.** On daily 2016 data, the fixed rule returns 8.61% versus 12.27% for buy-and-hold. Its largest peak-to-trough fall is 11.69% versus 18.92%. The chart shows net wealth from the recorded daily returns. |
| 0:58–1:13 | **Industry study.** Across 12 industry portfolios with equal starting capital in 2000–2016, annualised return is 6.14% versus 6.86% and maximum drawdown is −20.72% versus −47.09%. Cash earns the archive’s monthly rate. |
| 1:13–1:26 | **Uncertainty.** Resample paired blocks of 6, 12, or 24 months. All three 95% intervals for the annualised arithmetic mean return difference include zero. The intervals measure a different quantity from the compound annual returns in the previous chapter. |

Start with a single backtest, then reproduce the lag-1 experiment.

```bash
uv run quant-research examples/synthetic_prices.csv --test-start 2024-02-01
uv run quant-research --experiment examples/synthetic_experiment.json
```

`scripts/demo_reports.py` calls the existing synthetic recorder and experiment runner. It verifies the saved studies’ implementation hashes before reading the historical metrics, return paths, and uncertainty intervals. `demo-data.json` stores the synthetic inputs and runs, the declared comparison table, and the historical report hashes and derived equity curves. The film uses the results already published in the repository. To rerun the underlying research from its archived sources, follow the individual protocols. [AAPL pilot](STUDY_PLAN.md) · [Industry follow-up](FOLLOWUP_PLAN.md)

Ten basis points is 0.10% of value traded. A drawdown measures the fall from an earlier wealth peak. Both historical evaluations are retrospective, and both show lower return and shallower drawdown for the fixed rule. The AAPL table reports total return over one evaluation year. The industry table reports an annualised return over 17 years. [Research and accounting notes](RESEARCH.md)

## Validate

```bash
uv run --locked pytest
uv run --locked python scripts/check_report_provenance.py
uv run --locked ruff check .
uv run --locked ruff format --check .
ffprobe -v error -show_chapters docs/media/demo.mp4
ffmpeg -v error -i docs/media/demo.mp4 -f null -
ffmpeg -v error -i docs/media/preview.gif -f null -
```

When replacing the media, commit the MP4, GIF, and JSON together. Pin both README video links to that media commit. Encoded bytes can vary with FFmpeg and font versions.
