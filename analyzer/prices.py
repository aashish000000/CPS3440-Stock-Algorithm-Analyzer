"""Load adjusted closing prices and turn them into algorithm inputs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from analyzer.max_subarray import Subarray

# Prices are stored as integer micro-dollars so every algorithm sees the same
# exact differences. 1 dollar = 1_000_000 ticks.
TICKS_PER_DOLLAR = 1_000_000


@dataclass(frozen=True)
class Series:
    ticker: str
    dates: tuple[date, ...]
    ticks: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.dates) != len(self.ticks):
            raise ValueError(f"{self.ticker} dates and prices differ in length")


def price_to_ticks(price: float) -> int:
    return int(round(price * TICKS_PER_DOLLAR))


def ticks_to_dollars(ticks: int) -> float:
    return ticks / TICKS_PER_DOLLAR


def daily_changes(series: Series) -> list[int]:
    """Dollar change from each close to the next close, in ticks."""

    return [series.ticks[index] - series.ticks[index - 1] for index in range(1, len(series.ticks))]


def holding_return_bps(series: Series) -> int | None:
    """Buy-and-hold return in basis points. 100 basis points = 1 percent."""

    if len(series.ticks) < 2 or series.ticks[0] <= 0:
        return None
    return (series.ticks[-1] - series.ticks[0]) * 10_000 // series.ticks[0]


def window_bounds(series: Series, window: Subarray) -> tuple[date, date, int, int] | None:
    """Map a change-array window back to buy and sell closes.

    changes[i] is the move from dates[i] to dates[i + 1]. A window that sums
    changes[start..end] buys at dates[start] and sells at dates[end + 1].
    """

    if window.start is None or window.end is None:
        return None
    buy_at = window.start
    sell_at = window.end + 1
    return (series.dates[buy_at], series.dates[sell_at], series.ticks[buy_at], series.ticks[sell_at])


def slice_series(series: Series, since: date | None, until: date | None) -> Series:
    chosen = [
        (day, price)
        for day, price in zip(series.dates, series.ticks)
        if (since is None or day >= since) and (until is None or day <= until)
    ]
    if not chosen:
        return Series(series.ticker, (), ())
    days, prices = zip(*chosen)
    return Series(series.ticker, days, prices)


def parse_day(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def load_csv(path: Path) -> dict[str, Series]:
    """Read the downloaded Kaggle OHLCV file. Only Ticker, Date, and Adj Close are required."""

    grouped: dict[str, dict[date, int]] = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header row")
        fields = {name.strip(): name for name in reader.fieldnames}
        for needed in ("Ticker", "Date", "Adj Close"):
            if needed not in fields:
                raise ValueError(f"{path} is missing a {needed} column")
        for row in reader:
            ticker = (row[fields["Ticker"]] or "").strip().upper()
            raw_day = (row[fields["Date"]] or "").strip()
            raw_price = (row[fields["Adj Close"]] or "").strip()
            if not ticker or not raw_day or not raw_price:
                continue
            grouped.setdefault(ticker, {})[parse_day(raw_day[:10])] = price_to_ticks(float(raw_price))

    series = {
        ticker: Series(ticker, tuple(days), tuple(prices[day] for day in days))
        for ticker, prices in grouped.items()
        for days in [tuple(sorted(prices))]
        if prices
    }
    if not series:
        raise ValueError(f"{path} has no price rows")
    return series
