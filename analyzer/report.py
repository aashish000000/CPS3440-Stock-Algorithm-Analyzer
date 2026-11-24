"""Run every algorithm on one price file and render the comparison."""

from __future__ import annotations

import html
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from analyzer.max_subarray import ALGORITHMS as WINDOW_ALGORITHMS
from analyzer.max_subarray import COMPLEXITY as WINDOW_COMPLEXITY
from analyzer.max_subarray import Subarray
from analyzer.prices import (
    Series,
    daily_changes,
    holding_return_bps,
    load_csv,
    slice_series,
    ticks_to_dollars,
    window_bounds,
)
from analyzer.top_k import ALGORITHMS as TOP_ALGORITHMS
from analyzer.top_k import COMPLEXITY as TOP_COMPLEXITY
from analyzer.top_k import Scored


@dataclass(frozen=True)
class TimedWindow:
    name: str
    complexity: str
    seconds: float
    window: Subarray


@dataclass(frozen=True)
class TimedTop:
    name: str
    complexity: str
    seconds: float
    picked: tuple[Scored, ...]


@dataclass(frozen=True)
class Report:
    source: Path
    ticker: str
    since: date | None
    until: date | None
    series: Series
    windows: tuple[TimedWindow, ...]
    movers: tuple[TimedTop, ...]
    universe: int


def _time_call(function, *args):
    started = time.perf_counter()
    result = function(*args)
    return result, time.perf_counter() - started


def analyze(path: Path, ticker: str, k: int, since: date | None, until: date | None) -> Report:
    book = {symbol: slice_series(series, since, until) for symbol, series in load_csv(path).items()}
    book = {symbol: series for symbol, series in book.items() if len(series.ticks) >= 2}
    if not book:
        raise ValueError("No ticker has two prices in that date range")
    symbol = ticker.upper()
    if symbol not in book:
        sample = ", ".join(sorted(book)[:12])
        raise ValueError(f"{symbol} is not in {path}. Examples: {sample}")

    changes = daily_changes(book[symbol])
    windows: list[TimedWindow] = []
    for name, function in WINDOW_ALGORITHMS.items():
        window, seconds = _time_call(function, changes)
        windows.append(TimedWindow(name, WINDOW_COMPLEXITY[name], seconds, window))

    scored = []
    for item in book.values():
        score = holding_return_bps(item)
        if score is not None:
            scored.append(Scored(item.ticker, score))
    movers: list[TimedTop] = []
    for name, function in TOP_ALGORITHMS.items():
        picked, seconds = _time_call(function, scored, k)
        movers.append(TimedTop(name, TOP_COMPLEXITY[name], seconds, tuple(picked)))

    return Report(path, symbol, since, until, book[symbol], tuple(windows), tuple(movers), len(scored))


def _money(ticks: int) -> str:
    return f"${ticks_to_dollars(ticks):,.2f}"


def _percent_from_bps(bps: int) -> str:
    return f"{bps / 100:,.2f}%"


def _window_text(report: Report, window: Subarray) -> str:
    bounds = window_bounds(report.series, window)
    if bounds is None:
        return "no profitable buy/sell; stay out"
    buy_day, sell_day, buy_px, sell_px = bounds
    profit = sell_px - buy_px
    percent = (profit * 100) / buy_px if buy_px else 0
    return (
        f"buy {buy_day.isoformat()} at {_money(buy_px)}, "
        f"sell {sell_day.isoformat()} at {_money(sell_px)}, "
        f"profit {_money(profit)} per share ({percent:,.2f}%)"
    )


def render_text(report: Report) -> str:
    first_day = report.series.dates[0].isoformat()
    last_day = report.series.dates[-1].isoformat()
    lines = [
        f"Source: {report.source}",
        f"Tickers compared: {report.universe}",
        f"Best buy/sell window for {report.ticker} ({len(report.series.dates)} closes, {first_day} through {last_day})",
    ]
    if report.since or report.until:
        lines.append(f"Date filter: {report.since or 'start'} through {report.until or 'end'}")
    first = report.windows[0].window
    agreed = all(item.window == first for item in report.windows)
    for item in report.windows:
        lines.append(
            f"  {item.name:<20} {item.complexity:<14} {item.seconds * 1000:10.3f} ms   {_window_text(report, item.window)}"
        )
    lines.append("  Maximum-subarray algorithms agree." if agreed else "  Maximum-subarray algorithms disagree.")
    lines.append("")
    lines.append(f"Top {len(report.movers[0].picked)} movers by buy-and-hold return")
    top_sets = [item.picked for item in report.movers]
    top_agreed = all(picked == top_sets[0] for picked in top_sets)
    for item in report.movers:
        lines.append(f"  {item.name:<20} {item.complexity:<14} {item.seconds * 1000:10.3f} ms")
    lines.append("  Top-K algorithms agree." if top_agreed else "  Top-K algorithms disagree.")
    for rank, item in enumerate(report.movers[0].picked, start=1):
        lines.append(f"  {rank:>2}. {item.ticker:<8} {_percent_from_bps(item.score)}")
    return "\n".join(lines) + "\n"


def render_html(report: Report) -> str:
    first = report.windows[0].window
    window_rows = []
    for item in report.windows:
        window_rows.append(
            "<tr>"
            f"<td>{html.escape(item.name)}</td>"
            f"<td>{html.escape(item.complexity)}</td>"
            f"<td>{item.seconds * 1000:.3f} ms</td>"
            f"<td>{html.escape(_window_text(report, item.window))}</td>"
            "</tr>"
        )
    timing_rows = []
    for item in report.movers:
        timing_rows.append(
            "<tr>"
            f"<td>{html.escape(item.name)}</td>"
            f"<td>{html.escape(item.complexity)}</td>"
            f"<td>{item.seconds * 1000:.3f} ms</td>"
            "</tr>"
        )
    rank_rows = []
    for rank, item in enumerate(report.movers[0].picked, start=1):
        rank_rows.append(
            "<tr>"
            f"<td>{rank}</td>"
            f"<td>{html.escape(item.ticker)}</td>"
            f"<td>{html.escape(_percent_from_bps(item.score))}</td>"
            "</tr>"
        )
    agreed = all(item.window == first for item in report.windows)
    top_agreed = all(item.picked == report.movers[0].picked for item in report.movers)
    first_day = report.series.dates[0].isoformat()
    last_day = report.series.dates[-1].isoformat()
    span = f"<p>Adjusted closes from {first_day} through {last_day}.</p>"
    if report.since or report.until:
        span += f"<p>Date filter: {report.since or 'start'} through {report.until or 'end'}.</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Algorithm comparison</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 920px; margin: 40px auto; padding: 0 16px; line-height: 1.5; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; }}
th, td {{ border-bottom: 1px solid #ddd; text-align: left; padding: 6px 8px; vertical-align: top; }}
td:nth-child(3), th:nth-child(3) {{ white-space: nowrap; }}
</style>
</head>
<body>
<h1>Algorithm comparison</h1>
<p>Buy/sell search uses three maximum-subarray algorithms on daily adjusted-close changes. Top movers uses three top-K algorithms on buy-and-hold return. Prices come from {html.escape(str(report.source))} ({report.universe} tickers).</p>
{span}
<h2>Best buy/sell window for {html.escape(report.ticker)}</h2>
<p>{len(report.series.dates)} closing prices. {"All three algorithms found the same window." if agreed else "The algorithms did not agree."}</p>
<table>
<thead><tr><th>Algorithm</th><th>Complexity</th><th>Runtime</th><th>Result</th></tr></thead>
<tbody>
{"".join(window_rows)}
</tbody>
</table>
<h2>Top {len(report.movers[0].picked)} movers</h2>
<p>{"All three top-K algorithms returned the same ranking." if top_agreed else "The top-K algorithms did not agree."}</p>
<table>
<thead><tr><th>Algorithm</th><th>Complexity</th><th>Runtime</th></tr></thead>
<tbody>
{"".join(timing_rows)}
</tbody>
</table>
<table>
<thead><tr><th>Rank</th><th>Ticker</th><th>Buy-and-hold return</th></tr></thead>
<tbody>
{"".join(rank_rows)}
</tbody>
</table>
<p><a href="index.html">Back to the project page</a></p>
</body>
</html>
"""


def write_html(report: Report, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(report), encoding="utf-8")
