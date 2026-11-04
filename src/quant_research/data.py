"""Validated local single asset price observations, no network access or filling"""

import csv
from dataclasses import dataclass
from datetime import date
from math import isfinite
from pathlib import Path


@dataclass(frozen=True)
class PriceSeries:
    dates: tuple[date, ...]
    prices: tuple[float, ...]

    def __post_init__(self):
        object.__setattr__(self, "dates", tuple(self.dates))
        object.__setattr__(self, "prices", tuple(self.prices))

        if len(self.dates) != len(self.prices) or len(self.prices) < 2:
            raise ValueError("At least two matching dates and prices are required")

        if any(type(d) is not date for d in self.dates):
            raise ValueError("Dates must be calendar dates")

        if any(a >= b for a, b in zip(self.dates, self.dates[1:])):
            raise ValueError("Dates must be strictly increasing, without duplicates")

        validate_prices(self.prices)


def validate_prices(prices) -> None:
    if len(prices) < 2:
        raise ValueError("At least two prices are required")

    if any(
        isinstance(p, bool)
        or not isinstance(p, (int, float))
        or not isfinite(p)
        or p <= 0
        for p in prices
    ):
        raise ValueError("Prices must be finite positive numbers")


def load_prices(path: Path) -> PriceSeries:
    """Read ISO dates and adjusted_close, require consistent adjustment upstream"""
    dates, prices = [], []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []

        if len(fields) != len(set(fields)) or not {"date", "adjusted_close"} <= set(
            fields
        ):
            raise ValueError("CSV needs unique date and adjusted_close columns")
            
        for row_number, row in enumerate(reader, 2):
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("Malformed CSV row")
                dates.append(date.fromisoformat(row["date"]))
                prices.append(float(row["adjusted_close"]))
            except (ValueError, TypeError) as error:
                raise ValueError(f"CSV row {row_number}: {error}") from None

    return PriceSeries(tuple(dates), tuple(prices))
