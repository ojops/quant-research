# Coding conventions

These guidelines support reproducible financial calculations without unnecessary abstraction.

## Python

- Target Python 3.10; use four-space indentation and Ruff's 88-character formatting.
- Name functions and variables `snake_case`, classes `CapWords`, and constants `UPPER_CASE`.
- Use type annotations and concise docstrings at public interfaces where useful.
- Keep data loading, calculations and CLI reporting separate. Prefer straightforward structures.

## Research correctness

- State signal timing, execution assumptions, units and cost conventions explicitly.
- Validate input prices; do not silently fill, reorder or adjust them.
- Use floating-point arithmetic and tolerance-aware numerical tests.
- Keep signals causal: a signal can depend only on prices observed by its timestamp.
- Comment on **why** a decision matters, not on obvious operations.

## Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Apply formatting using `uv run ruff format .`. Type checking and docstring linting are not mandatory CI gates. Keep formatting-only edits separate from algorithm changes where practical.
