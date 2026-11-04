# Coding conventions

The project follows the same core Python conventions as [Meal Plan Calculator](https://github.com/ojops/meal-plan-calc) and [Rubik's Cube Simulator](https://github.com/ojops/rubiks-sim), while keeping financial research-specific requirements separate.

## Formatting and imports

- Use Python 3.10-compatible syntax and four-space indentation.
- Name functions and variables `snake_case`, classes `CapWords`, and constants `UPPER_CASE`.
- Let Ruff enforce an 88-character line length, import sorting and spacing between module-level definitions.
- Group imports as standard library, third-party packages, then local modules.
- Separate distinct ideas with blank lines; avoid hand-aligning code or adding whitespace after every statement.

## Documentation and types

- Give public functions concise action-oriented docstrings.
- Explain units, mutations, return values and errors when they are not obvious.
- Use type annotations at public interfaces and for non-obvious result structures, without annotating every trivial helper or test.
- Prefer comments that explain **why** a choice was made, especially for signal timing, financial assumptions, units and cost accounting.
- Avoid comments that merely repeat a line of code. Use ordinary sentences and consistent capitalisation.

## Design and correctness

- Keep calculations separate from terminal output and input parsing.
- Validate external inputs and reject invalid data with clear errors; never silently fill unknown prices.
- Use small dataclasses when several related results belong together.
- Use binary floating-point arithmetic for time-series analysis and tolerance-aware tests. Do not replace it with `Decimal` merely because another repository uses `Decimal` for food quantities.
- Make chronology explicit: signals may only depend on information available at the time they are produced.
- Treat hypothetical fills and cost models as assumptions, not proof of achievable trading results.
- Keep formatting-only changes separate from behavioural or mathematical changes where practical.

## Development checks

From the repository root:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

To apply formatting rather than only check it:

```bash
uv run ruff format .
```

Ruff is pinned to version 0.14.3 and configured for Python 3.10, 88 columns, import sorting and basic syntax/unused-code checks (`E4`, `E7`, `E9`, `F`, `I`). There is no mandatory all-annotations rule, docstring linter or additional type-checking gate.
