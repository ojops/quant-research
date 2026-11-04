# Coding conventions

## Formatting and imports

- Use Python 3.10 compatible syntax and four space indentation
- Name functions and variables `snake_case`, classes `CapWords`, and constants `UPPER_CASE`
- Let Ruff enforce an 88 character line length, import sorting and spacing between module level definitions
- Group imports as standard library, third party packages, then local modules

## Documentation and types

- Give public functions concise action oriented docstrings
- Explain units, mutations, return values and errors when they are not obvious
- Use type annotations at public interfaces and for non obvious result structures, without annotating every trivial helper or test
- Prefer comments that explain **why** a choice was made, especially for signal timing, financial assumptions, units, and cost accounting

## Design and correctness

- Keep calculations separate from terminal output and input parsing
- Validate external inputs and reject invalid data with clear errors, never silently fill unknown prices
- Use small dataclasses when several related results belong together
- Use binary floating point arithmetic for time series analysis and tolerance aware tests
- Make chronology explicit: signals may only depend on information available at the time they are produced

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

Keep documentation and formatting separate from algorithm changes where practical. There is no mandatory type checking or docstring linting gate.
