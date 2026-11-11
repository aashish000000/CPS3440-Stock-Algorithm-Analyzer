"""Command line: python -m analyzer --ticker AAPL --k 10

The default CSV is data/SP500_Historical_Data.csv, the file downloaded from
the Kaggle dataset jacksaleeby/s-and-p500-historical-data (original name
SP500_Historical_Data.csv).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyzer.prices import parse_day
from analyzer.report import analyze, render_text, write_html

# Downloaded Kaggle export. Gitignored because the CSV is about 143 MB.
DEFAULT_DATA = Path("data/SP500_Historical_Data.csv")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare max-subarray and top-K algorithms on the downloaded Kaggle S&P 500 CSV.")
    parser.add_argument(
        "data",
        nargs="?",
        type=Path,
        default=DEFAULT_DATA,
        help="OHLCV CSV with Ticker, Date, and Adj Close columns (default: the downloaded Kaggle file data/SP500_Historical_Data.csv)",
    )
    parser.add_argument("--ticker", default="AAPL", help="Ticker used for the buy/sell window (default: AAPL)")
    parser.add_argument("--k", type=int, default=10, help="How many top movers to list (default: 10)")
    parser.add_argument("--since", help="First date to include, YYYY-MM-DD")
    parser.add_argument("--until", help="Last date to include, YYYY-MM-DD")
    parser.add_argument("--html", type=Path, help="Also write an HTML results page")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.k < 0:
        print("--k must be zero or greater", file=sys.stderr)
        return 2
    data = args.data if args.data is not None else DEFAULT_DATA
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
