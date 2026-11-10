"""Command line: python -m analyzer --fetch data/sp500.csv --ticker AAPL --k 10"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzer.fetch import date_stamp, download_history
from analyzer.prices import parse_day
from analyzer.report import analyze, render_text, write_html


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare max-subarray and top-K algorithms on S&P 500 prices.")
    parser.add_argument("data", nargs="?", type=Path, help="OHLCV CSV with Ticker, Date, and Adj Close columns")
    parser.add_argument("--fetch", type=Path, metavar="PATH", help="Download Yahoo Finance S&P 500 history to this CSV, then analyze it")
    parser.add_argument("--ticker", default="AAPL", help="Ticker used for the buy/sell window (default: AAPL)")
    parser.add_argument("--k", type=int, default=10, help="How many top movers to list (default: 10)")
    parser.add_argument("--since", help="First date to include, YYYY-MM-DD")
    parser.add_argument("--until", help="Last date to include, YYYY-MM-DD")
    parser.add_argument("--max-symbols", type=int, help="Download only the first N S&P 500 symbols")
    parser.add_argument("--html", type=Path, help="Also write an HTML results page")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.k < 0:
        print("--k must be zero or greater", file=sys.stderr)
        return 2
    data = args.data
    if args.fetch is not None:
        rows, failed = download_history(
            args.fetch,
            date_stamp("2015-01-01"),
            date_stamp("2026-02-21"),
            max_symbols=args.max_symbols,
        )
        print(f"Wrote {rows} rows to {args.fetch}", flush=True)
        for message in failed:
            print(f"skipped {message}", file=sys.stderr)
        data = args.fetch
    if data is None:
        print("Pass a CSV path or --fetch PATH", file=sys.stderr)
        return 2
    since = parse_day(args.since) if args.since else None
    until = parse_day(args.until) if args.until else None
    if since and until and since > until:
        print("--since is after --until", file=sys.stderr)
        return 2
    try:
        report = analyze(data, args.ticker, args.k, since, until)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    sys.stdout.write(render_text(report))
    if args.html is not None:
        write_html(report, args.html)
        print(f"Wrote {args.html}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
