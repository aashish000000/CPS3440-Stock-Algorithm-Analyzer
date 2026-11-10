"""Optional fallback: download a fresh S&P 500 history from Yahoo Finance.

The project's measurements use the downloaded Kaggle CSV
jacksaleeby/s-and-p500-historical-data. That file's original name is
SP500_Historical_Data.csv (Ticker, Date, Open, High, Low, Close, Adj Close,
Volume; 2,703,531 rows; 472 tickers; 2000-01-03 through 2026-02-20). This
module does not recreate that file. It writes a shorter current-constituent
history in a similar column layout when the Kaggle export is unavailable:

    Ticker,Date,Open,High,Low,Close,Adj Close,Volume
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&period1={start}&period2={end}"
USER_AGENT = "Mozilla/5.0 CPS3440-stock-algorithm-analyzer"
_SYMBOL = re.compile(r"^[A-Z]{1,5}(?:-[A-Z])?$")


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503}:
                raise
        except urllib.error.URLError as error:
            last_error = error
        time.sleep(0.8 * (attempt + 1))
    assert last_error is not None
    raise last_error


def parse_constituent_symbols(html: str) -> list[str]:
    """Read ticker symbols from the constituents table only.

    The page also has a sector navbox after that table. Those rows are company
    names, so parsing stops at the first closing table tag. Dots become the
    dashes Yahoo Finance uses (BRK.B -> BRK-B).
    """

    start = html.find('id="constituents"')
    if start < 0:
        raise RuntimeError("Could not find the S&P 500 constituents table")
    end = html.find("</table>", start)
    if end < 0:
        raise RuntimeError("Could not find the end of the constituents table")
    table = html[start:end]
    symbols: list[str] = []
    for row in re.findall(r"<tr\b.*?</tr>", table, flags=re.S):
        cell = re.search(r"<td\b[^>]*>(.*?)</td>", row, flags=re.S)
        if cell is None:
            continue
        text = re.sub(r"<[^>]+>", "", cell.group(1))
        symbol = text.strip().upper().replace(".", "-")
        if _SYMBOL.fullmatch(symbol) and symbol not in symbols:
            symbols.append(symbol)
    return symbols


def load_sp500_symbols() -> list[str]:
    """Current S&P 500 symbols from Wikipedia."""

    symbols = parse_constituent_symbols(_get(WIKI_URL).decode("utf-8", "replace"))
    if len(symbols) < 400:
        raise RuntimeError(f"Expected about 500 symbols, found {len(symbols)}")
    return symbols


def _number(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def fetch_symbol(symbol: str, period_start: int, period_end: int) -> list[dict[str, str]]:
    payload = json.loads(_get(CHART_URL.format(symbol=symbol, start=period_start, end=period_end)))
    chart = payload.get("chart", {})
    if chart.get("error"):
        raise RuntimeError(f"{symbol}: {chart['error']}")
    result = chart.get("result") or []
    if not result:
        raise RuntimeError(f"{symbol}: empty chart")
    block = result[0]
    stamps = block.get("timestamp") or []
    quote = (block.get("indicators") or {}).get("quote", [{}])[0]
    adjusted = (block.get("indicators") or {}).get("adjclose", [{}])[0].get("adjclose") or []
    rows: list[dict[str, str]] = []
    for index, stamp in enumerate(stamps):
        adj = adjusted[index] if index < len(adjusted) else None
        if adj is None:
            continue
        day = datetime.fromtimestamp(stamp, timezone.utc).date().isoformat()
        rows.append(
            {
                "Ticker": symbol,
                "Date": day,
                "Open": _number(quote.get("open", [None])[index] if quote.get("open") else None),
                "High": _number(quote.get("high", [None])[index] if quote.get("high") else None),
                "Low": _number(quote.get("low", [None])[index] if quote.get("low") else None),
                "Close": _number(quote.get("close", [None])[index] if quote.get("close") else None),
                "Adj Close": str(adj),
                "Volume": _number(quote.get("volume", [None])[index] if quote.get("volume") else None),
            }
        )
    if not rows:
        raise RuntimeError(f"{symbol}: no adjusted closes")
    return rows


def download_history(path: Path, period_start: int, period_end: int, max_symbols: int | None = None) -> tuple[int, list[str]]:
    """Write one CSV for the current S&P 500. Returns (row count, failed symbols)."""

    symbols = load_sp500_symbols()
    if max_symbols is not None:
        symbols = symbols[:max_symbols]
    rows: list[dict[str, str]] = []
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_symbol, symbol, period_start, period_end): symbol for symbol in symbols}
        done = 0
        for future in as_completed(futures):
            symbol = futures[future]
            done += 1
            try:
                rows.extend(future.result())
            except Exception as error:  # noqa: BLE001 - keep going so one symbol cannot abort the file
                failed.append(f"{symbol}: {error}")
            if done % 25 == 0 or done == len(symbols):
                print(f"fetched {done}/{len(symbols)}", flush=True)
    rows.sort(key=lambda row: (row["Ticker"], row["Date"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Ticker", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), failed


def date_stamp(value: str) -> int:
    day = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(day.timestamp())
