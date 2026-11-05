# Reproducing the portfolio demonstration

`media/demo.mp4` is a 38-second silent film, 1920 × 1080 at 30 FPS,
encoded as H.264/yuv420p with fast-start metadata. `media/demo.gif` shows
the entire 38-second film at its original pace, at 768 × 432 and 10 FPS,
looping directly in the README. There is no shortened excerpt.

Both media files are tracked in Git. The animation uses a relative link;
the MP4 link uses a raw GitHub URL pinned to its media commit to avoid
branch-dependent redirects. When regenerating and committing a new MP4,
update the pinned README links to that commit. The link opens or downloads
the MP4 depending on the browser; the README animation itself has no
play/pause controls. No external hosting service is required.

From the repository root, with Python 3.10 and uv:

```bash
uv sync --locked --extra demo
uv run --locked --extra demo python scripts/render_demo.py
```

Install FFmpeg with libx264 and DejaVu Sans/Mono (Ubuntu: `ffmpeg` and
`fonts-dejavu-core`). Pillow 12.3.0 is the only new dependency, in the optional
`demo` extra. The research calculations still use the standard library. Rendering
is local, CPU-based and does not require a display or a market-data connection.

Use `--output-dir /path/to/output` for an alternate destination. For four
chapter snapshots without encoding:

```bash
uv run --locked --extra demo python scripts/render_demo.py --stills-only --output-dir /tmp/quant-demo-stills
```

## Data and calculations

The entire film uses the existing `examples/synthetic_prices.csv`: 60 weekday
observations from 2024-01-01 to 2024-03-22. It is a deterministic mathematical
series, **not real prices or evidence of investment performance**.

`quant_research.demo_data.build_demo()` invokes the production `main()` CLI for
each declared configuration and captures its JSON. It uses the existing
`momentum_weights`, `simple_returns` and `equity_curve` functions for signal and
chart paths. It does not reimplement backtest accounting or estimate new metrics.
Every CLI path, metric, setting and input checksum is preserved in
`media/demo-data.json`, with equity paths added for plotting.

All runs evaluate 36 return intervals from 2024-02-01 to 2024-03-22 with earlier
prices supplying history. Both strategy and benchmark start flat and pay their
applicable entry costs. Fixed variants are declared in the generator:

| Lookback | Cost (bps) | Strategy total return in the recorded synthetic run |
| --- | --- | --- |
| 5 | 0 | +5.72% |
| 5 | 10 | +5.20% |
| 5 | 50 | +3.11% |
| 3 | 10 | +8.61% |
| 10 | 10 | −2.66% |

All variants are shown; there is no automated fitting or selection of a winner.
Changing assumptions after viewing this synthetic series is illustrative
sensitivity analysis, not untouched out-of-sample validation.

| Time | Demonstration |
| --- | --- |
| 0–9 s | Input prices, history/evaluation boundary and next-interval long/cash ribbon |
| 9–18 s | The 7 February cash signal and the following interval, including the 10 bps exit fee |
| 18–28 s | Actual net strategy and buy-and-hold equity, drawdown, volatility, Sharpe and turnover |
| 28–38 s | Three cost assumptions and three lookback choices, with every declared variant displayed |

The timing example uses 31 January's close (103.7719) and 7 February's close
(102.6201) to choose cash. The following asset return is −0.908%; the strategy
return is −0.100% because it pays to exit. The signal never earns the price
change that created it. This still assumes idealised trading at the observed
signal close, not a realistic next-session execution model.

The film labels the dataset as synthetic throughout. Annualised volatility and
zero-risk-free Sharpe use 252 periods per year over only 36 intervals. They are
descriptive outputs with no statistical-significance claim. Cash earns zero,
there is one asset, and no final liquidation is forced. See [RESEARCH.md](RESEARCH.md).

## Validation

```bash
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
ffmpeg -v error -i docs/media/demo.mp4 -f null -
ffmpeg -v error -i docs/media/demo.gif -f null -
```

The completed run passed 24 tests, Ruff lint and formatting. Recording tests
compare paths and metrics with the actual CLI, check the cash/exit-fee interval,
verify a shared horizon and all sensitivity variants, and confirm reproducible
JSON. Representative encoded frames were inspected for axis labels, units,
timing and clipping. Five pre-existing whitespace-only formatting failures were
also corrected; no core calculation behaviour changed.

Chart lines reveal observations for presentation; the accompanying metrics are
explicitly labelled as the completed run, not live partial-period estimates.
Encoded bytes can vary across FFmpeg and font versions even when JSON is identical.
