"""Time the algorithms on the downloaded Kaggle S&P 500 CSV and count the work they do.

The default file is data/SP500_Historical_Data.csv from
jacksaleeby/s-and-p500-historical-data (original name SP500_Historical_Data.csv).
That is the file the benchmark measures. The Yahoo Finance fetcher is an
optional fallback and is not used here.

Wall-clock trials use the production functions. A second metric, operation
count, is exact: inner-loop iterations for the maximum-subarray scans, and
comparisons for Top-K. Brute force above 10,000 records is not timed. Its
operation count is still exact, and its runtime is the n^2 projection fitted
to the largest size that was timed.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from pathlib import Path

from analyzer.max_subarray import brute_force, divide_and_conquer, kadane
from analyzer.prices import daily_changes, load_csv
from analyzer.top_k import Scored, _sort_key, top_k_heap, top_k_sort

SIZES = (1_000, 10_000, 100_000, 1_000_000)
BRUTE_FORCE_LIMIT = 10_000
DEFAULT_TRIALS = 5
DEFAULT_K = 10


def brute_iterations(n: int) -> int:
    """Every start/end pair. This is Theta(n^2) in every case."""

    return n * (n + 1) // 2


def kadane_iterations(n: int) -> int:
    return n


def divide_and_conquer_iterations(n: int) -> int:
    """Element reads in the crossing scans and the base cases.

    The closed form is not needed: one dry run is O(n log n) and finishes
    quickly even at n = 1,000,000. The count itself does not depend on the
    values, only on n, so the input can be zeros.
    """

    if n <= 0:
        return 0
    reads = 0

    def crossing(low: int, mid: int, high: int) -> None:
        nonlocal reads
        for _ in range(mid, low - 1, -1):
            reads += 1
        for _ in range(mid + 1, high + 1):
            reads += 1

    def divide(low: int, high: int) -> None:
        nonlocal reads
        if low == high:
            reads += 1
            return
        mid = (low + high) // 2
        divide(low, mid)
        divide(mid + 1, high)
        crossing(low, mid, high)

    divide(0, n - 1)
    return reads


def heap_comparisons(items: list[Scored], k: int) -> int:
    """Comparisons made by the production heap algorithm on this input."""

    if k <= 0 or not items:
        return 0
    count = 0

    class _Node:
        __slots__ = ("item",)

        def __init__(self, item: Scored) -> None:
            self.item = item

        def __lt__(self, other: _Node) -> bool:
            nonlocal count
            count += 1
            if self.item.score != other.item.score:
                return self.item.score < other.item.score
            return self.item.ticker > other.item.ticker

    import heapq

    heap: list[_Node] = []
    for item in items:
        node = _Node(item)
        if len(heap) < k:
            heapq.heappush(heap, node)
        elif heap[0] < node:
            heapq.heapreplace(heap, node)
    return count


def sort_comparisons(items: list[Scored], k: int) -> int:
    if k <= 0 or not items:
        return 0
    count = 0

    class _Key:
        __slots__ = ("item",)

        def __init__(self, item: Scored) -> None:
            self.item = item

        def __lt__(self, other: _Key) -> bool:
            nonlocal count
            count += 1
            return _sort_key(self.item) < _sort_key(other.item)

    ordered = sorted((_Key(item) for item in items), key=lambda wrapper: wrapper)
    # sorted(key=) compares keys. Using the wrapper as its own key counts
    # those comparisons. The slice does no further ordering work.
    del ordered[:k]
    return count


def _median(samples: list[float]) -> float:
    return statistics.median(samples)


def _time_call(function, argument, trials: int) -> dict[str, float]:
    samples = []
    for _ in range(trials):
        started = time.perf_counter()
        function(argument)
        samples.append((time.perf_counter() - started) * 1000)
    return {
        "trials": trials,
        "median_ms": _median(samples),
        "min_ms": min(samples),
        "max_ms": max(samples),
        "samples_ms": samples,
    }


def _peak_bytes(function, argument) -> int:
    tracemalloc.start()
    function(argument)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def load_market_records(path: Path) -> tuple[list[int], list[Scored], dict]:
    """Daily changes and scored moves from the downloaded Kaggle CSV.

    The summary is taken from the file that was read: row count, ticker
    count, and date range. The default path is the Kaggle export, not a
    Yahoo Finance refetch.
    """

    book = load_csv(path)
    changes: list[int] = []
    moves: list[Scored] = []
    for ticker in sorted(book):
        series = book[ticker]
        deltas = daily_changes(series)
        changes.extend(deltas)
        for index, delta in enumerate(deltas):
            previous = series.ticks[index]
            if previous <= 0:
                continue
            moves.append(Scored(f"{ticker}:{index}", delta * 10_000 // previous))
    if len(changes) < SIZES[-1] or len(moves) < SIZES[-1]:
        raise ValueError(
            f"{path} has {len(changes)} changes and {len(moves)} moves; need at least {SIZES[-1]}"
        )
    dates = [day for series in book.values() for day in series.dates]
    summary = {
        "path": path.as_posix(),
        "filename": path.name,
        "original_filename": "SP500_Historical_Data.csv",
        "kaggle_dataset": "jacksaleeby/s-and-p500-historical-data",
        "kaggle_url": "https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data",
        "columns": ["Ticker", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"],
        "rows": sum(len(series.dates) for series in book.values()),
        "tickers": len(book),
        "date_min": min(dates).isoformat(),
        "date_max": max(dates).isoformat(),
        "source": "downloaded Kaggle CSV",
    }
    return changes, moves, summary


def _quadratic_prediction(measured_ms: dict[int, float]) -> dict[str, float]:
    """Project untimed sizes from the largest measured median.

    The caller stores milliseconds. An earlier version treated those
    milliseconds as seconds and multiplied by 1,000 again, which inflated
    the 100,000- and 1,000,000-record projections by 1000. The constant
    below is milliseconds per n², and predicted_ms is in milliseconds.
    """

    anchor = max(measured_ms)
    ms_per_n_squared = measured_ms[anchor] / (anchor * anchor)
    predicted_ms = {
        str(size): ms_per_n_squared * size * size
        for size in SIZES
        if size not in measured_ms
    }
    return {
        "anchor_n": anchor,
        "ms_per_n_squared": ms_per_n_squared,
        "seconds_per_n_squared": ms_per_n_squared / 1000.0,
        "predicted_ms": predicted_ms,
    }


def run_max_subarray(changes: list[int], trials: int) -> dict:
    report: dict = {"algorithms": {}, "agreement": {}}
    brute_times: dict[int, float] = {}
    for size in SIZES:
        sample = changes[:size]
        kadane_window = kadane(sample)
        divide_window = divide_and_conquer(sample)
        agreement = {"kadane_equals_divide_and_conquer": kadane_window == divide_window}
        if size <= BRUTE_FORCE_LIMIT:
            agreement["brute_force_equals_kadane"] = brute_force(sample) == kadane_window
        report["agreement"][str(size)] = agreement

        window_functions = {
            "kadane": kadane,
            "divide_and_conquer": divide_and_conquer,
        }
        if size <= BRUTE_FORCE_LIMIT:
            window_functions = {"brute_force": brute_force, **window_functions}
        for name, function in window_functions.items():
            print(f"timing {name} n={size} trials={trials}", flush=True)
            timed = _time_call(function, sample, trials)
            timed["operations"] = {
                "brute_force": brute_iterations(size),
                "divide_and_conquer": divide_and_conquer_iterations(size),
                "kadane": kadane_iterations(size),
            }[name]
            timed["peak_bytes"] = _peak_bytes(function, sample)
            timed["executed"] = True
            report["algorithms"].setdefault(name, {})[str(size)] = timed
            if name == "brute_force":
                brute_times[size] = timed["median_ms"]
        if size > BRUTE_FORCE_LIMIT:
            report["algorithms"].setdefault("brute_force", {})[str(size)] = {
                "executed": False,
                "operations": brute_iterations(size),
                "reason": f"A full O(n^2) trial is timed only through n={BRUTE_FORCE_LIMIT}.",
            }
    report["brute_force_prediction"] = _quadratic_prediction(brute_times)
    for size, milliseconds in report["brute_force_prediction"]["predicted_ms"].items():
        report["algorithms"]["brute_force"][size]["predicted_median_ms"] = milliseconds
    return report


def _time_top(function, items: list[Scored], k: int, trials: int) -> dict[str, float]:
    samples = []
    for _ in range(trials):
        started = time.perf_counter()
        function(items, k)
        samples.append((time.perf_counter() - started) * 1000)
    return {
        "trials": trials,
        "median_ms": _median(samples),
        "min_ms": min(samples),
        "max_ms": max(samples),
        "samples_ms": samples,
    }


def run_top_k(moves: list[Scored], k: int, trials: int) -> dict:
    report: dict = {"k": k, "algorithms": {}}
    orders = ("random", "best_for_heap", "worst_for_heap")
    for size in SIZES:
        base = moves[:size]
        prepared = {
            "random": base,
            "best_for_heap": sorted(base, key=_sort_key),
            "worst_for_heap": sorted(base, key=_sort_key, reverse=True),
        }
        print(f"timing top-k n={size} k={k}", flush=True)
        for name, function, counter in (
            ("full_sort", top_k_sort, sort_comparisons),
            ("binary_heap", top_k_heap, heap_comparisons),
        ):
            for order in orders:
                items = prepared[order]
                timed = _time_top(function, items, k, trials)
                timed["operations"] = counter(items, k)
                timed["peak_bytes"] = _peak_bytes(lambda values: function(values, k), items)
                timed["executed"] = True
                timed["agree_with_sort"] = function(items, k) == top_k_sort(items, k)
                report["algorithms"].setdefault(name, {}).setdefault(order, {})[str(size)] = timed
    return report


def write_figures(results: dict, directory: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    directory.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    sizes = results["sizes"]

    def series(algorithm: str, field: str, predicted: bool = False) -> list[float | None]:
        rows = results["max_subarray"]["algorithms"][algorithm]
        values: list[float | None] = []
        for size in sizes:
            row = rows[str(size)]
            if predicted:
                values.append(row.get("predicted_median_ms"))
            elif row.get("executed"):
                values.append(row[field])
            else:
                values.append(None)
        return values

    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    for name, style in (
        ("brute_force", "o-"),
        ("divide_and_conquer", "s-"),
        ("kadane", "^-"),
    ):
        measured = series(name, "median_ms")
        axis.plot(
            [size for size, value in zip(sizes, measured) if value is not None],
            [value for value in measured if value is not None],
            style,
            label=name.replace("_", " "),
        )
    brute_rows = results["max_subarray"]["algorithms"]["brute_force"]
    predicted_sizes = []
    predicted_times = []
    for size in sizes:
        row = brute_rows[str(size)]
        if row.get("executed"):
            anchor = (size, row["median_ms"])
        elif row.get("predicted_median_ms") is not None:
            predicted_sizes.append(size)
            predicted_times.append(row["predicted_median_ms"])
    if predicted_sizes:
        axis.plot(
            [anchor[0], *predicted_sizes],
            [anchor[1], *predicted_times],
            "o--",
            color="tab:blue",
            alpha=0.75,
            label="brute force predicted",
        )
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlabel("Records from the S&P 500 file")
    axis.set_ylabel("Median runtime (ms)")
    axis.set_title("Maximum subarray: measured time against size")
    axis.grid(True, which="both", linestyle=":", alpha=0.6)
    axis.legend(fontsize=8)
    figure.tight_layout()
    path = directory / "max-subarray-time.png"
    figure.savefig(path, dpi=140)
    plt.close(figure)
    written.append(str(path))

    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    for name, style in (
        ("brute_force", "o-"),
        ("divide_and_conquer", "s-"),
        ("kadane", "^-"),
    ):
        operations = [results["max_subarray"]["algorithms"][name][str(size)]["operations"] for size in sizes]
        axis.plot(sizes, operations, style, label=name.replace("_", " "))
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlabel("Records")
    axis.set_ylabel("Element reads or pair iterations")
    axis.set_title("Maximum subarray: operation count")
    axis.grid(True, which="both", linestyle=":", alpha=0.6)
    axis.legend(fontsize=8)
    figure.tight_layout()
    path = directory / "max-subarray-ops.png"
    figure.savefig(path, dpi=140)
    plt.close(figure)
    written.append(str(path))

    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    for name, style in (("full_sort", "o-"), ("binary_heap", "s-")):
        medians = [
            results["top_k"]["algorithms"][name]["random"][str(size)]["median_ms"] for size in sizes
        ]
        axis.plot(sizes, medians, style, label=name.replace("_", " "))
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlabel("Daily-move records")
    axis.set_ylabel("Median runtime (ms)")
    axis.set_title(f"Top-{results['top_k']['k']} on random market order")
    axis.grid(True, which="both", linestyle=":", alpha=0.6)
    axis.legend()
    figure.tight_layout()
    path = directory / "topk-time.png"
    figure.savefig(path, dpi=140)
    plt.close(figure)
    written.append(str(path))

    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    width = 0.35
    positions = list(range(len(sizes)))
    best = [results["top_k"]["algorithms"]["binary_heap"]["best_for_heap"][str(size)]["median_ms"] for size in sizes]
    worst = [results["top_k"]["algorithms"]["binary_heap"]["worst_for_heap"][str(size)]["median_ms"] for size in sizes]
    axis.bar([position - width / 2 for position in positions], best, width, label="best case (top K first)")
    axis.bar([position + width / 2 for position in positions], worst, width, label="worst case (every insert)")
    axis.set_xticks(positions, [f"{size:,}" for size in sizes])
    axis.set_yscale("log")
    axis.set_ylabel("Median runtime (ms)")
    axis.set_title("Heap Top-K: best case versus worst case")
    axis.legend(fontsize=8)
    figure.tight_layout()
    path = directory / "heap-cases.png"
    figure.savefig(path, dpi=140)
    plt.close(figure)
    written.append(str(path))
    return written


def build_results(changes: list[int], moves: list[Scored], trials: int, k: int) -> dict:
    return {
        "trials": trials,
        "sizes": list(SIZES),
        "brute_force_timed_through": BRUTE_FORCE_LIMIT,
        "source_changes": len(changes),
        "source_moves": len(moves),
        "max_subarray": run_max_subarray(changes, trials),
        "top_k": run_top_k(moves, k, trials),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark the downloaded Kaggle S&P 500 CSV.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/SP500_Historical_Data.csv"),
        help="Downloaded Kaggle CSV (default: data/SP500_Historical_Data.csv from jacksaleeby/s-and-p500-historical-data)",
    )
    parser.add_argument("--out", type=Path, default=Path("benchmarks/results.json"))
    parser.add_argument("--figures", type=Path, default=Path("docs/assets"))
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    args = parser.parse_args(argv)
    changes, moves, dataset = load_market_records(args.data)
    print(
        f"loaded {dataset['rows']} rows, {dataset['tickers']} tickers, "
        f"{dataset['date_min']} through {dataset['date_max']}",
        flush=True,
    )
    print(f"loaded {len(changes)} changes and {len(moves)} moves", flush=True)
    results = build_results(changes, moves, args.trials, args.k)
    results["dataset"] = dataset
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    figures = write_figures(results, args.figures)
    print(f"wrote {args.out}")
    for figure in figures:
        print(f"wrote {figure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
