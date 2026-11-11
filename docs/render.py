"""Build the GitHub Pages site and the technical paper from benchmark JSON."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "results.json"
DOCS = ROOT / "docs"
SITE = "https://aashish000000.github.io/CPS3440-Stock-Algorithm-Analyzer/"

DEMO = """Source: data/SP500_Historical_Data.csv
Tickers compared: 472
Best buy/sell window for AAPL (6573 closes, 2000-01-03 through 2026-02-20)
  brute_force          O(n^2)           8364.118 ms   buy 2002-10-08 at $0.20, sell 2025-12-02 at $285.92, profit $285.72 per share (142,860.00%)
  divide_and_conquer   O(n log n)          9.029 ms   buy 2002-10-08 at $0.20, sell 2025-12-02 at $285.92, profit $285.72 per share (142,860.00%)
  kadane               O(n)                2.487 ms   buy 2002-10-08 at $0.20, sell 2025-12-02 at $285.92, profit $285.72 per share (142,860.00%)
  Maximum-subarray algorithms agree.

Top 10 movers by buy-and-hold return
  full_sort            O(n log n)          0.114 ms
  binary_heap          O(n log k)          0.122 ms
  quickselect          O(n) average        0.231 ms
  Top-K algorithms agree.
   1. NVDA     210,811.11%
   2. MNST     209,300.00%
   3. AXON     94,228.26%
   4. DECK     79,026.66%
   5. TPL      75,639.39%
   6. NFLX     65,458.33%
   7. ODFL     42,748.93%
   8. TSCO     33,000.00%
   9. AAPL     31,397.61%
  10. AVGO     29,079.82%
"""


def load() -> dict:
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def fmt_ms(value: float, projected: bool = False) -> str:
    label = f"{value / 3_600_000:.1f} h" if value >= 3_600_000 else (
        f"{value / 60_000:.1f} min" if value >= 60_000 else (
            f"{value / 1000:.2f} s" if value >= 1000 else f"{value:.3f} ms"
        )
    )
    return label + (" projected" if projected else "")


def fmt_ops(value: int) -> str:
    if value >= 1_000_000_000:
        return f"{value:.3e}"
    return f"{value:,}"


def window_row(results: dict, name: str, size: int) -> dict:
    return results["max_subarray"]["algorithms"][name][str(size)]


def top_row(results: dict, name: str, order: str, size: int) -> dict:
    return results["top_k"]["algorithms"][name][order][str(size)]


def clock(row: dict) -> str:
    if row.get("executed"):
        return fmt_ms(row["median_ms"])
    if "predicted_median_ms" in row:
        return fmt_ms(row["predicted_median_ms"], projected=True)
    return "not timed"


def slope(results: dict, name: str, small: int, large: int) -> str:
    left = window_row(results, name, small)
    right = window_row(results, name, large)
    if not (left.get("executed") and right.get("executed")):
        return "n/a"
    if left["median_ms"] <= 0 or right["median_ms"] <= 0:
        return "n/a"
    value = math.log(right["median_ms"] / left["median_ms"]) / math.log(large / small)
    return f"{value:.2f}"


def top_slope(results: dict, name: str, small: int, large: int) -> str:
    left = top_row(results, name, "random", small)
    right = top_row(results, name, "random", large)
    if left["median_ms"] <= 0 or right["median_ms"] <= 0:
        return "n/a"
    value = math.log(right["median_ms"] / left["median_ms"]) / math.log(large / small)
    return f"{value:.2f}"


STYLE = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Source Sans 3", "Segoe UI", sans-serif; color: #1c2430; background: #f6f4ef; line-height: 1.55; }
header.site { background: #14342b; color: #f6f4ef; padding: 28px 20px 18px; }
header.site h1 { margin: 0 0 6px; font-family: Georgia, serif; font-weight: 600; font-size: 1.8rem; }
header.site p { margin: 0; max-width: 760px; }
nav { position: sticky; top: 0; background: #102820; padding: 8px 12px; z-index: 2; }
nav a { color: #e7f2ec; text-decoration: none; margin: 4px 9px 4px 0; display: inline-block; font-size: 0.92rem; }
nav a:hover { text-decoration: underline; }
main { max-width: 980px; margin: 0 auto; padding: 8px 20px 64px; }
section { padding-top: 22px; }
h2 { font-family: Georgia, serif; font-size: 1.55rem; border-bottom: 1px solid #d5d0c6; padding-bottom: 4px; }
h3 { font-family: Georgia, serif; font-size: 1.15rem; margin-bottom: 6px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 18px; background: white; font-size: 0.95rem; }
th, td { border-bottom: 1px solid #e4dfd4; text-align: left; padding: 6px 8px; vertical-align: top; }
th { background: #e7efe9; }
pre { background: #12211c; color: #f3f7f4; padding: 12px 14px; overflow-x: auto; font-size: 0.86rem; line-height: 1.4; }
code { font-family: "IBM Plex Mono", ui-monospace, monospace; }
img.figure { width: 100%; max-width: 760px; background: white; border: 1px solid #e4dfd4; }
img.qr { width: 180px; height: auto; background: white; border: 1px solid #e4dfd4; }
.note { font-size: 0.92rem; color: #3d4a44; }
a { color: #0f5c4c; }
"""

PAPER_STYLE = """
@page { size: letter; margin: 0.8in; }
body { font-family: Georgia, "Times New Roman", serif; color: #1a1a1a; font-size: 11pt; line-height: 1.38; max-width: 7.1in; margin: 0.4in auto; }
h1 { font-size: 16pt; text-align: center; margin-bottom: 4px; }
.authors, .meta { text-align: center; margin: 0; font-size: 11pt; }
h2 { font-size: 13pt; margin-top: 16px; }
h3 { font-size: 11.5pt; margin-bottom: 4px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9.5pt; }
th, td { border: 1px solid #bbb; padding: 3px 5px; text-align: left; }
th { background: #f0f0f0; }
pre { font-family: "Courier New", monospace; font-size: 8.5pt; background: #f7f7f7; padding: 6px; white-space: pre-wrap; }
img { width: 88%; display: block; margin: 8px auto 2px; }
p.caption { font-size: 9.5pt; margin: 0 0 10px; color: #333; }
p { margin: 0.45em 0; }
"""


def window_table(results: dict) -> str:
    sizes = results["sizes"]
    header = "".join(f"<th>{size:,}</th>" for size in sizes)
    rows = []
    for name in ("brute_force", "divide_and_conquer", "kadane"):
        cells = []
        for size in sizes:
            row = window_row(results, name, size)
            cells.append(f"<td>{html.escape(clock(row))}<br>ops {fmt_ops(row['operations'])}</td>")
        rows.append(f"<tr><td>{name.replace('_', ' ')}</td>{''.join(cells)}</tr>")
    return f"<table><thead><tr><th>Algorithm</th>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def top_table(results: dict, order: str) -> str:
    sizes = results["sizes"]
    header = "".join(f"<th>{size:,}</th>" for size in sizes)
    rows = []
    for name in ("full_sort", "binary_heap", "quickselect"):
        cells = []
        for size in sizes:
            row = top_row(results, name, order, size)
            cells.append(
                f"<td>{html.escape(fmt_ms(row['median_ms']))}<br>comps {fmt_ops(row['operations'])}</td>"
            )
        rows.append(f"<tr><td>{name.replace('_', ' ')}</td>{''.join(cells)}</tr>")
    return f"<table><thead><tr><th>Algorithm</th>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def _ns(row: dict) -> str:
    if "ns_per_pair" in row:
        return f"{row['ns_per_pair']:.0f} ns"
    if row.get("operations") and row.get("median_ms") is not None:
        return f"{row['median_ms'] * 1_000_000 / row['operations']:.0f} ns"
    return "n/a"


def dependence_paragraph(results: dict) -> str:
    market_1k = window_row(results, "brute_force", 1000)
    market_10k = window_row(results, "brute_force", 10000)
    market_100k = window_row(results, "brute_force", 100000)
    zero = results.get("brute_force_data_dependence", {}).get("zero_mean", {}).get("sizes", {})
    machine = results.get("environment", {})
    machine_line = ""
    if machine:
        machine_line = (
            f" The timings were taken on Python {html.escape(str(machine.get('python', '')))}"
            f" ({html.escape(str(machine.get('cpu', '')))})."
        )
    zero_line = ""
    if "1000" in zero and "10000" in zero:
        zero_line = (
            f" The same function on zero-mean uniform integers took {_ns(zero['1000'])} per pair at 1,000 records"
            f" and {_ns(zero['10000'])} per pair at 10,000."
        )
    return (
        "The time per pair is not a fixed constant. On the market prefix it moved from "
        f"{_ns(market_1k)} at 1,000 records to {_ns(market_10k)} at 10,000 and {_ns(market_100k)} at 100,000. "
        "A positive window allocates a candidate, and a longer prefix of Python integers also stops fitting in cache. "
        "The pair count is still exactly n(n+1)/2."
        + zero_line
        + " Zero-mean data does not remove the cost: many of those windows are still positive, and the values are large."
        + machine_line
    )


def build_site(results: dict) -> str:
    k = results["top_k"]["k"]
    trials = results["trials"]
    changes = results["source_changes"]
    moves = results["source_moves"]
    growth = (
        f"From 1,000 to 10,000 records the measured exponents were "
        f"{slope(results, 'brute_force', 1000, 10000)} for brute force (model 2), "
        f"{slope(results, 'divide_and_conquer', 1000, 10000)} for divide and conquer (model about 1.2), and "
        f"{slope(results, 'kadane', 1000, 10000)} for Kadane (model 1). "
        f"From 1,000 to 1,000,000 the sort exponent was {top_slope(results, 'full_sort', 1000, 1000000)} "
        f"and the heap exponent was {top_slope(results, 'binary_heap', 1000, 1000000)}."
    )
    brute_10k = window_row(results, "brute_force", 10000)
    kadane_10k = window_row(results, "kadane", 10000)
    ratio = brute_10k["median_ms"] / kadane_10k["median_ms"] if kadane_10k["median_ms"] else 0
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stock Market Algorithm Analyzer</title>
<style>{STYLE}</style>
</head>
<body>
<header class="site">
<h1>Historical Stock Market Algorithm Analyzer</h1>
<p>CPS 3440 group project. Three maximum-subarray algorithms and three Top-K algorithms, measured on the downloaded Kaggle S&amp;P 500 CSV.</p>
</header>
<nav>
<a href="#home">Home</a>
<a href="#problem">Problem</a>
<a href="#dataset">Dataset</a>
<a href="#solution">Solution</a>
<a href="#algorithms">Algorithms</a>
<a href="#complexity">Complexity</a>
<a href="#results">Results</a>
<a href="#demo">Demo</a>
<a href="#technologies">Technologies</a>
<a href="#team">Team</a>
<a href="#resources">Resources</a>
</nav>
<main>
<section id="home">
<h2>Home</h2>
<p>This project asks a trading question with algorithms from an analysis course. Given daily adjusted closes, what single buy and later sell would have made the most money per share, and which records were the largest movers? We answer the first question with brute force, divide and conquer, and Kadane's scan. We answer the second with merge sort, a size-K heap, and quickselect. The command-line tool checks that the algorithms agree. The benchmark then times them at 1,000, 10,000, 100,000, and 1,000,000 records drawn from the market file.</p>
<p>On Apple, across 6,573 closes from 3 January 2000 through 20 February 2026, every maximum-subarray algorithm returns the same window: buy on 8 October 2002 at $0.20 and sell on 2 December 2025 at $285.92, a profit of $285.72 per share. Among 472 stocks in the downloaded Kaggle file, NVDA has the largest buy-and-hold return, 210,811.11 percent.</p>
<p>The write-up of pseudocode, proofs, and case-by-case bounds is in <a href="algorithms.md">algorithms.md</a>. The technical paper is <a href="paper.html">paper.html</a> (<a href="paper.pdf">PDF</a>). Slides are in the repository under <code>presentation/</code>.</p>
<p><img class="qr" src="assets/site-qr.png" alt="QR code for the GitHub Pages site"><br><span class="note">QR code for this site: {html.escape(SITE)}</span></p>
</section>
<section id="problem">
<h2>Problem</h2>
<p>Let the adjusted closes be P[0], P[1], …, P[n]. Define the daily change A[i] = P[i+1] − P[i]. The sum of A[start] through A[end] equals P[end+1] − P[start]. The best buy/sell window is a maximum subarray of A. If every subarray is negative, the best decision is not to trade.</p>
<p>Top-K takes a list of scored records and returns the K best. The order is higher score first. Equal scores break toward the earlier name, so sort and heap can be compared exactly. In the product run, a record is one stock's buy-and-hold return. In the scaling study, a record is one daily move, because the file has more than a million of those and 472 stocks.</p>
</section>
<section id="dataset">
<h2>Dataset</h2>
<p>The measurements were run on the downloaded <a href="https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data">Kaggle S&amp;P 500 OHLC file</a>. The original filename is SP500_Historical_Data.csv. Columns are Ticker, Date, Open, High, Low, Close, Adj Close, and Volume. The file has 2,703,531 rows, 472 tickers, and dates from 2000-01-03 through 2026-02-20. Download steps are in <code>data/README.md</code>.</p>
<p>The benchmark file has {changes:,} daily changes and {moves:,} scored daily moves, from those 472 constituents, 3 January 2000 through 20 February 2026. Adjusted close is stored as an integer number of micro-dollars. The algorithms therefore compare identical integers, not rounded floats.</p>
<p>Prefixes of that pool are the 1K, 10K, 100K, and 1M record inputs. The same prefix is reused for every trial, so the spread across trials is measurement noise rather than a new random draw.</p>
</section>
<section id="solution">
<h2>Solution</h2>
<p>The program is a standard-library Python package, <code>analyzer</code>. <code>prices.py</code> loads the CSV and turns closes into changes. <code>max_subarray.py</code> holds the three window algorithms. <code>top_k.py</code> holds the sort and the heap. <code>__main__.py</code> is the command-line tool. <code>benchmark.py</code> runs the scaling study.</p>
<pre><code>python3 -m analyzer data/SP500_Historical_Data.csv --ticker AAPL --k 10
python3 -m analyzer.benchmark --data data/SP500_Historical_Data.csv</code></pre>
<p>A correct window is not only the largest sum. It is the earliest such window. All three window routines share that rule, and the unit tests include the CLRS example, all-negative arrays, and random arrays where the three answers must match. Sort and heap are checked the same way, including ties.</p>
</section>
<section id="algorithms">
<h2>Algorithms</h2>
<h3>Brute force, Θ(n²)</h3>
<pre><code>prefix[0] = 0
for i in 0..n-1: prefix[i+1] = prefix[i] + A[i]
for start in 0..n-1:
    for end in start..n-1:
        consider prefix[end+1] - prefix[start]</code></pre>
<p>Every window is scored exactly once. The prefix makes each score O(1), so the double loop is quadratic rather than cubic. Correctness is the claim that the best pair is the best window. Best, average, and worst time are the same because every pair is visited. Extra space is the prefix, Θ(n).</p>
<h3>Divide and conquer, Θ(n log n)</h3>
<pre><code>if one element: return it when positive, else no trade
mid = (low + high) // 2
return the best of
    DIVIDE(low, mid),
    DIVIDE(mid+1, high),
    best suffix of the left half + best prefix of the right half</code></pre>
<p>Any optimal window is entirely left of mid, entirely right of mid, or it crosses mid. A crossing window is a left suffix plus a right prefix, and both of those are found with a linear scan. The recurrence T(n) = 2T(n/2) + Θ(n) solves to Θ(n log n) in every case. The call stack is Θ(log n).</p>
<h3>Kadane, Θ(n)</h3>
<pre><code>current = 0
for i in 0..n-1:
    if current &lt; 0: restart at i
    current += A[i]
    keep [start, i] when it is the best positive window so far</code></pre>
<p>A negative running sum is thrown away because appending it to a later element cannot help. The optimal window itself never contains a point where the sum from its start is negative, or a suffix of that window would be better. One pass is enough. Best, average, and worst time are Θ(n), and extra space is Θ(1). A linear scan is optimal: an unread element can change the answer.</p>
<h3>Top-K by sorting, and Top-K by a heap</h3>
<pre><code>SORT: order by score descending, name ascending, and keep K
HEAP: min-heap of the K weakest survivors
      push until the heap is full
      replace the minimum when a better record arrives
      sort those K at the end</code></pre>
<p>Sorting is correct because a total order puts the answer in the first K positions. Merge sort is Θ(n log n) in the best, average, and worst case. The heap invariant says every rejected record is worse than the current minimum. Its worst case is Θ(n log k), when every arrival enters the heap. Its best case is Θ(n + k log k), when the first K records are already the answer. Extra heap space is Θ(k). Quickselect is the third method: average Θ(n), worst Θ(n²), then a merge sort of the surviving K. The study uses k = {k}.</p>
</section>
<section id="complexity">
<h2>Complexity</h2>
<table>
<thead><tr><th>Algorithm</th><th>Best time</th><th>Average time</th><th>Worst time</th><th>Extra space</th></tr></thead>
<tbody>
<tr><td>Brute-force subarray</td><td>Θ(n²)</td><td>Θ(n²)</td><td>Θ(n²)</td><td>Θ(n)</td></tr>
<tr><td>Divide and conquer</td><td>Θ(n log n)</td><td>Θ(n log n)</td><td>Θ(n log n)</td><td>Θ(log n)</td></tr>
<tr><td>Kadane</td><td>Θ(n)</td><td>Θ(n)</td><td>Θ(n)</td><td>Θ(1)</td></tr>
<tr><td>Top-K merge sort</td><td>Θ(n log n)</td><td>Θ(n log n)</td><td>Θ(n log n)</td><td>Θ(n)</td></tr>
<tr><td>Top-K heap</td><td>Θ(n + k log k)</td><td>Θ(n log k) bound</td><td>Θ(n log k)</td><td>Θ(k)</td></tr>
<tr><td>Quickselect</td><td>Θ(n)</td><td>Θ(n)</td><td>Θ(n²)</td><td>Θ(log n)</td></tr>
</tbody>
</table>
<p class="note">The heap's average bound is a safe upper bound. On random scores with a fixed k, most late records lose one comparison against the root and never enter the heap, so the measured curve can sit close to linear. The worst-case input in the benchmark forces an insertion on every record.</p>
</section>
<section id="results">
<h2>Results</h2>
<p>Each timed cell through 10,000 records is the median of {trials} trials on the same records. Brute force at 100,000 records is one trial. The second line is the operation count: pair iterations for brute force, element reads for divide and conquer, loop iterations for Kadane, and comparisons for Top-K. Only the 1,000,000-record brute-force time is an n² projection, taken from the measured 100,000-record trial, and it is labeled projected. At 10,000 records the brute-force median was about {ratio:.0f} times Kadane's median ({html.escape(fmt_ms(brute_10k["median_ms"]))} versus {html.escape(fmt_ms(kadane_10k["median_ms"]))}). The measured 100,000-record brute-force time is {html.escape(clock(window_row(results, "brute_force", 100000)))}. The projection at 1,000,000 records is {html.escape(clock(window_row(results, "brute_force", 1000000)))}.</p>
<p>{dependence_paragraph(results)}</p>
<p>{growth}</p>
<h3>Maximum subarray</h3>
{window_table(results)}
<img class="figure" src="assets/max-subarray-time.png" alt="Log-log plot of maximum-subarray runtime versus number of records">
<img class="figure" src="assets/max-subarray-ops.png" alt="Log-log plot of maximum-subarray operation counts versus number of records">
<p class="note">Solid marks were timed. Brute force at 100,000 records is one trial. The dashed brute-force segment is the 1,000,000-record projection. The operation plot has no projection: n(n+1)/2 is exact at every size, and the divide-and-conquer count is from a dry recursion that does not depend on the values.</p>
<h3>Top-{k}, records in market order</h3>
{top_table(results, "random")}
<img class="figure" src="assets/topk-time.png" alt="Log-log plot of merge sort, heap, and quickselect runtime on market-ordered records">
<h3>Heap best case and worst case</h3>
<p>Best case puts the true top {k} first. Worst case feeds improving scores so every record enters the heap.</p>
<table>
<thead><tr><th>Heap input</th>{"".join(f"<th>{size:,}</th>" for size in results["sizes"])}</tr></thead>
<tbody>
<tr><td>Best case</td>{"".join(f"<td>{html.escape(fmt_ms(top_row(results, 'binary_heap', 'best_for_heap', size)['median_ms']))}<br>comps {fmt_ops(top_row(results, 'binary_heap', 'best_for_heap', size)['operations'])}</td>" for size in results["sizes"])}</tr>
<tr><td>Random</td>{"".join(f"<td>{html.escape(fmt_ms(top_row(results, 'binary_heap', 'random', size)['median_ms']))}<br>comps {fmt_ops(top_row(results, 'binary_heap', 'random', size)['operations'])}</td>" for size in results["sizes"])}</tr>
<tr><td>Worst case</td>{"".join(f"<td>{html.escape(fmt_ms(top_row(results, 'binary_heap', 'worst_for_heap', size)['median_ms']))}<br>comps {fmt_ops(top_row(results, 'binary_heap', 'worst_for_heap', size)['operations'])}</td>" for size in results["sizes"])}</tr>
</tbody>
</table>
<img class="figure" src="assets/heap-cases.png" alt="Bar chart comparing best-case and worst-case heap runtime">
<p>Comparison counts follow the case analysis more cleanly than the clock does. At one million records the best-case heap makes {fmt_ops(top_row(results, "binary_heap", "best_for_heap", 1000000)["operations"])} comparisons and the worst-case heap makes {fmt_ops(top_row(results, "binary_heap", "worst_for_heap", 1000000)["operations"])}, because every arrival is inserted. The random-order heap also makes about n comparisons, so it is the easy case in the comparison model. Its wall-clock time is nevertheless the fastest of the three at 100,000 and 1,000,000 records. The best-case and worst-case inputs are permutations of the original Python objects, and scanning those pointers is less local than scanning the array in allocation order. The operation column is the one that confirms best versus worst. The clock column is the one a user would feel, and it should not be described as a pure Θ(n log k) curve on market order.</p>
<p>On the 472-stock product question the three window algorithms agreed, and sort, heap, and quickselect agreed. That check is separate from the scaling study: Apple has 6,573 closes (6,572 changes) in the Kaggle file, and the ranking has 472 stocks. Quickselect is in the tool, the tests, and the scaling table beside merge sort and the heap.</p>
</section>
<section id="demo">
<h2>Demo</h2>
<p>From the repository root, with Python 3.12:</p>
<pre><code>python3 -m unittest discover -s tests
python3 -m analyzer tests/fixtures/sample.csv --ticker AAPL --k 3
python3 -m analyzer data/SP500_Historical_Data.csv --ticker AAPL --k 10</code></pre>
<p>The sample fixture is committed, so the tests and the small demo do not need the network. The full run below used the downloaded Kaggle CSV at <code>data/SP500_Historical_Data.csv</code>. One run on the Kaggle file printed:</p>
<pre><code>{html.escape(DEMO)}</code></pre>
</section>
<section id="technologies">
<h2>Technologies</h2>
<ul>
<li>Python 3.12. The analyzer, the tests, and the benchmark timer use the standard library.</li>
<li>unittest for the agreement tests and the operation-count checks.</li>
<li>matplotlib for the four figures. It is listed in <code>requirements.txt</code> and is not imported by the trading tool.</li>
<li>GitHub Pages serves this <code>docs/</code> directory.</li>
<li>The downloaded Kaggle CSV <code>SP500_Historical_Data.csv</code> for every reported measurement. See <code>data/README.md</code>.</li>
</ul>
</section>
<section id="team">
<h2>Team</h2>
<table>
<thead><tr><th>Name</th><th>What to ask this person about</th></tr></thead>
<tbody>
<tr><td>Aashish Joshi</td><td><code>prices.py</code> and <code>__main__.py</code>: loading adjusted closes, the micro-dollar representation, and the command-line report.</td></tr>
<tr><td>Aron Dardouri</td><td>Brute force in <code>max_subarray.py</code> and <code>benchmark.py</code>: the double loop, the trial harness, the measured 100,000-record trial, and the labeled 1,000,000-record projection.</td></tr>
<tr><td>Bhartendra Kumar Mandal</td><td>Divide and conquer in <code>max_subarray.py</code>: the crossing scan, the recurrence, and the earliest-window tie rule.</td></tr>
<tr><td>Brian Lucero</td><td><code>top_k.py</code>: the size-K heap, the total order used by the sort, and the best-case versus worst-case heap trials.</td></tr>
</tbody>
</table>
<p>Resume lines for each person are in <a href="../CONTRIBUTIONS.md">CONTRIBUTIONS.md</a> in the repository. The presentation script names the speaker on every slide.</p>
</section>
<section id="resources">
<h2>Resources</h2>
<ul>
<li><a href="https://github.com/aashish000000/CPS3440-Stock-Algorithm-Analyzer">GitHub repository</a></li>
<li><a href="{html.escape(SITE)}">This site</a></li>
<li><a href="https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data">Kaggle S&amp;P 500 historical data</a></li>
<li>Cormen, Leiserson, Rivest, and Stein, <em>Introduction to Algorithms</em>, maximum-subarray chapter.</li>
<li>Bentley, <em>Programming Pearls</em>, the one-pass maximum-subarray scan often credited to Kadane.</li>
<li>Merge sort and a hand-written binary heap in <code>analyzer/top_k.py</code>.</li>
<li><a href="https://kean.smartcatalogiq.com/en/2026-2027/undergraduate-catalog/courses/cps-computer-science/3000/cps-3440">CPS 3440 catalog description</a></li>
<li><a href="paper.html">Technical paper</a> and <a href="algorithms.md">full pseudocode and proofs</a></li>
</ul>
</section>
</main>
</body>
</html>
"""


def build_paper(results: dict) -> str:
    k = results["top_k"]["k"]
    trials = results["trials"]
    ratio_10k = window_row(results, "brute_force", 10000)["median_ms"] / window_row(results, "kadane", 10000)["median_ms"]
    heap_1m = top_row(results, "binary_heap", "random", 1_000_000)
    sort_1m = top_row(results, "full_sort", "random", 1_000_000)
    heap_worst_1m = top_row(results, "binary_heap", "worst_for_heap", 1_000_000)
    heap_best_1m = top_row(results, "binary_heap", "best_for_heap", 1_000_000)
    sort_best_1m = top_row(results, "full_sort", "best_for_heap", 1_000_000)
    sort_worst_1m = top_row(results, "full_sort", "worst_for_heap", 1_000_000)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Algorithmic efficiency on S&amp;P 500 history</title>
<style>{PAPER_STYLE}</style>
</head>
<body>
<h1>Finding One Trade and the Top Movers:<br>Maximum Subarray and Top-K on S&amp;P 500 History</h1>
<p class="authors">Aashish Joshi, Aron Dardouri, Bhartendra Kumar Mandal, and Brian Lucero</p>
<p class="meta">CPS 3440 Analysis of Algorithms, Kean University</p>

<h2>1. Introduction</h2>
<p>A price series looks like a finance problem and an algorithms problem at the same time. Once daily changes replace prices, the best single buy and a later sell is the maximum-subarray problem: find a contiguous block whose sum is at least as large as every other block. Ranking records is the selection problem called Top-K. Both problems have several correct algorithms whose asymptotic costs are far apart. This paper implements those algorithms, proves the versions we ship, and measures them on prefixes of the downloaded Kaggle CSV at 1,000, 10,000, 100,000, and 1,000,000 records.</p>
<p>The implementations are brute force, the CLRS divide-and-conquer recurrence, and Kadane's one-pass scan, plus Top-K by merge sort, a size-{k} binary heap, and quickselect. Each algorithm is stated in pseudocode, with a correctness argument and best, average, and worst-case time and space. The experiment reports two metrics. The first is wall-clock time: the median of {trials} trials through 10,000 records, and one brute-force trial at 100,000 records. The second is an operation count: pair iterations, element reads, or comparisons. Brute force is not executed at 1,000,000 records. That runtime is an n² projection from the 100,000-record measurement and is marked as a projection. The operation count at that size is still exact.</p>
<p>The last sections separate a slow algorithm from a hard problem. Maximum subarray is in P. A cardinality-constrained portfolio problem built on the same prices is NP-hard. Speeding up the Python loops does not change that classification. Four course reflections, labeled A through D, close the paper. They match the catalog topics of CPS 3440: asymptotic analysis, divide and conquer, advanced data structures, and NP-completeness.</p>

<h2>2. Problem and data</h2>
<p>Let P be adjusted closing prices. The change array is A[i] = P[i+1] − P[i], stored as an integer number of micro-dollars. Then A[start] + … + A[end] = P[end+1] − P[start]. We return the maximum positive sum and, among such windows, the earliest start and then the earliest end. If no positive window exists, the result is the empty trade, profit 0. That rule is part of the specification, not an accident of one implementation, because the three programs are required to return the same object.</p>
<p>Top-K uses the total order (higher score, then earlier name). In the command-line report the score is the buy-and-hold return of one stock, in basis points, and there are 472 scores. That n is too small for a scaling plot. The scaling study therefore scores every day-to-day move in the file. There are {results["source_moves"]:,} such records. A prefix of length n is a legal Top-K instance: "which K daily moves were the largest?" It is a different product question from the 472-stock ranking, and the paper does not pretend otherwise. It is the same algorithm on real market numbers at the four required sizes.</p>
<p>Every measurement in this paper was run on the downloaded Kaggle CSV <code>SP500_Historical_Data.csv</code> from <code>jacksaleeby/s-and-p500-historical-data</code>. Columns are Ticker, Date, Open, High, Low, Close, Adj Close, and Volume. The file has 2,703,531 rows, 472 tickers, and dates from 3 January 2000 through 20 February 2026.</p>

<h2>3. Algorithms</h2>
<h3>3.1 Brute force</h3>
<pre>prefix[0] ← 0
for i ← 0 to n−1: prefix[i+1] ← prefix[i] + A[i]
for start ← 0 to n−1:
    for end ← start to n−1:
        consider prefix[end+1] − prefix[start]</pre>
<p>By induction, the prefix difference equals the window sum, so every nonempty window is considered exactly once. The retained window is optimal under the earliest-window rule, and a fully negative array leaves the empty trade in place. Time is Θ(n²) in the best, average, and worst case, because the loops do not depend on the values. Extra space is the prefix, Θ(n). A running-sum formulation uses Θ(1) extra words and the same quadratic bound. We keep the prefix form because each window is then a subtraction rather than a restarted addition, which is the version that was timed.</p>
<h3>3.2 Divide and conquer</h3>
<pre>DIVIDE(low, high):
    if low = high: return the element when it is positive, else no trade
    mid ← floor((low+high)/2)
    return best of DIVIDE(low, mid), DIVIDE(mid+1, high), CROSS(low, mid, high)
CROSS: maximum suffix ending at mid, plus maximum prefix starting at mid+1</pre>
<p>Proof by induction on the length of the interval. A one-element interval is immediate. For a longer interval, an optimal window is wholly on the left, wholly on the right, or it contains both mid and mid+1. The recursive calls return optimal answers for the halves. A crossing window must be some suffix of the left half plus some prefix of the right half, and the two scans maximize those pieces, breaking ties toward the earlier index. The best of the three candidates is therefore optimal for the whole interval. The recurrence T(n) = 2T(n/2) + Θ(n), with T(1) = Θ(1), solves to Θ(n log n) by the Master Theorem. Every input pays the same scans, so best, average, and worst time agree. Extra space is the Θ(log n) recursion stack.</p>
<h3>3.3 Kadane</h3>
<pre>current ← 0; start ← 0; best ← empty
for i ← 0 to n−1:
    if current &lt; 0: current ← 0; start ← i
    current ← current + A[i]
    if current &gt; 0: keep the better of best and [start, i]</pre>
<p>Suppose a positive optimal window is [p, q]. The running sum from p cannot become negative at any r inside the window. If it did, [r+1, q] would beat [p, q]. Kadane therefore does not reset inside [p, q], and when the index reaches q the current sum is at least the optimal sum. The recorded best cannot exceed every real window sum, so it is optimal. The empty result covers arrays with no positive window. The loop is Θ(n) in every case and uses Θ(1) extra words. The bound is asymptotically tight for this problem, because any correct algorithm must inspect every entry.</p>
<h3>3.4 Sort and heap</h3>
<pre>SORT(items, k): sort by (−score, name) and return the first k
HEAP(items, k): min-heap of size at most k, worst record at the root
    push while the heap has room
    if the next record beats the root, replace the root
    sort the surviving k records</pre>
<p>The sort is correct because it realizes a total order. Merge sort solves T(n) = 2T(n/2) + Θ(n), so best, average, and worst time are Θ(n log n), with Θ(n) extra space. An already ordered list does not fall to linear time. The heap maintains a different invariant: after it fills, every record left outside is worse than the root. A record that belongs in the final answer can be rejected only if k better records are already inside, which is a contradiction. Worst-case time is Θ(n log k), when every record enters. Best-case time is Θ(n + k log k), when nothing after the first k records enters. Extra space is Θ(k) plus the final merge sort of those k items. For random scores and a small fixed k, the expected number of successful insertions after the heap fills is far below n, so a measured "average" can look closer to linear than to n log k. We report that as a fact about expectation, not as a replacement for the worst-case bound. Quickselect places the kth record in average linear time and worst-case quadratic time, then merge-sorts those k records.</p>

<h2>4. Method</h2>
<p>The production functions are the ones timed. An instrumented twin is used only for comparison counts, where the count depends on the data. Pair iterations for brute force are n(n+1)/2. Kadane iterations are n. Divide-and-conquer reads are counted by a recursion on the indexes alone, so they do not depend on prices and can be evaluated at n = 1,000,000 in negligible time. Each timing trial calls the function on the same prefix. We report the median, and the raw samples are stored in <code>results/results.json</code> together with the Python version and the CPU. Peak traced memory is recorded once per cell with <code>tracemalloc</code>, as a check that the space column is not fiction, but the official second metric is the operation count.</p>
<p>Brute force at 100,000 records is one trial, about half an hour in this interpreter. Five trials at that size would not change the shape of the curve, and five trials at 1,000,000 records would be days. The constant c in c·n² is the 100,000-record time divided by 100000². The 1,000,000-record cell uses that constant and is labeled projected. Figures draw that point with a dashed line. Calling a projection a measurement would make the theory-versus-observed section dishonest.</p>
<p>{dependence_paragraph(results)} The 1,000,000-record projection uses the measured 100,000-record market trial, so it already includes that market-data constant. It is still a projection.</p>
<p>Heap inputs have three shapes. Market order is the order the file produced, used as the ordinary case. Best case puts the true top K first, so later records should lose one comparison against the root and never enter. Worst case feeds scores from low to high so each arrival replaces the root. Merge sort and quickselect are timed on those same three arrangements. Merge sort does not become linear on a sorted layout: every size still pays Θ(n log n) comparisons. The clock can still move because the prepared layouts are permutations and lose the allocation-order locality of the original prefix. Both columns are reported so that a comparison count is not silently rewritten as a runtime.</p>

<h2>5. Measurements</h2>
<p>At 10,000 changes, the brute-force median was {fmt_ms(window_row(results, "brute_force", 10000)["median_ms"])} and Kadane's median was {fmt_ms(window_row(results, "kadane", 10000)["median_ms"])}, about {ratio_10k:.0f} times faster for the linear scan. Divide and conquer at that size took {fmt_ms(window_row(results, "divide_and_conquer", 10000)["median_ms"])}. The log-log slope of median time from 1,000 to 10,000 records is {slope(results, "brute_force", 1000, 10000)} for brute force, {slope(results, "divide_and_conquer", 1000, 10000)} for divide and conquer, and {slope(results, "kadane", 1000, 10000)} for Kadane. A pure power n² has slope 2, a pure line has slope 1, and n log n sits a little above 1 on a short range. From 10,000 to 1,000,000, Kadane's slope is {slope(results, "kadane", 10000, 1000000)} and divide-and-conquer's slope is {slope(results, "divide_and_conquer", 10000, 1000000)}.</p>
{window_table(results)}
<img src="assets/max-subarray-time.png" alt="Runtime of the three maximum-subarray algorithms">
<p class="caption">Figure 1. Median runtime. Sizes through 10,000 records are five-trial medians. Brute force at 100,000 records is one trial. The dashed segment is the n² projection to 1,000,000 records and was not timed.</p>
<img src="assets/max-subarray-ops.png" alt="Operation counts of the three maximum-subarray algorithms">
<p class="caption">Figure 2. Operation counts. Brute-force pair iterations are n(n+1)/2 at every size, including the sizes that were not timed. Divide-and-conquer reads come from a dry recursion on the indexes.</p>
<p>The operation plot is the cleaner Big-O picture. Brute-force iterations grow by about 100 each time n grows by 10, which is the square: 500,500 pairs at 1,000 records and 50,005,000 pairs at 10,000. Kadane's count is exactly n. Divide-and-conquer reads grow slightly faster than linear, as n log n requires: 10,976 reads at 1,000 records and 20,951,424 reads at 1,000,000. The clock does not copy those exponents exactly. Divide and conquer's wall-clock slope from 10,000 to 1,000,000 records is {slope(results, "divide_and_conquer", 10000, 1000000)}, nearer a line than the read-count slope on the same range. Python recursion allocates a result object on every call, and that linear traffic is large next to the extra log factor. The paper therefore does not claim that the clock alone measured the Master Theorem. It claims that the read count follows the recurrence, that the clock stays far below the quadratic projection, and that Kadane remains the practical algorithm. A slope estimated from two sizes can miss a model by a few tenths when a constant term is present. The operation column is what we trust when the clock and the model disagree by that amount.</p>
<p>At one million daily moves, with k = {k}, the random-order sort median was {fmt_ms(sort_1m["median_ms"])} and the random-order heap median was {fmt_ms(heap_1m["median_ms"])}. Sort made {fmt_ops(sort_1m["operations"])} comparisons and the heap scan made {fmt_ops(heap_1m["operations"])}. The heap's best-case median at that size was {fmt_ms(heap_best_1m["median_ms"])} and its worst-case median was {fmt_ms(heap_worst_1m["median_ms"])}. Slopes from 1,000 to 1,000,000 records on market order were {top_slope(results, "full_sort", 1000, 1000000)} for the sort and {top_slope(results, "binary_heap", 1000, 1000000)} for the heap.</p>
{top_table(results, "random")}
<img src="assets/topk-time.png" alt="Merge sort, heap, and quickselect on market order">
<p class="caption">Figure 3. Merge sort, heap, and quickselect on the market-order prefix. All three were timed at every size.</p>
<img src="assets/heap-cases.png" alt="Best-case and worst-case heap times">
<p class="caption">Figure 4. Heap wall-clock time on the prepared best-case and worst-case layouts. Comparison counts, not these bars alone, are the case split: at one million records the best case does {fmt_ops(heap_best_1m["operations"])} comparisons and the worst case does {fmt_ops(heap_worst_1m["operations"])}.</p>
<p>The product run is the small-n check that the finance answer is stable. On Apple's 6,573 closes in the Kaggle file the three window algorithms returned buy 8 October 2002 at $0.20 and sell 2 December 2025 at $285.92, profit $285.72 per share. On 472 buy-and-hold returns, sort and heap returned the same top 10, led by NVDA at 210,811.11 percent. Quickselect matched them as well. Those identities are unit-tested on synthetic arrays, including the CLRS figure whose maximum subarray sums to 43.</p>

<h2>6. Theory versus what the clock did</h2>
<p>Where the model is a tight Θ bound that does not depend on the data, the measurements follow it. Brute force's exponent from 1,000 to 10,000 records is {slope(results, "brute_force", 1000, 10000)}, next to the model value 2. The 100,000-record point is a measurement rather than a second projection, and its operation count is exactly n(n+1)/2. Kadane's operation count is exactly n, and its wall-clock slope from 1,000 to 1,000,000 records is {slope(results, "kadane", 1000, 1000000)}. The first step is already near 1. Fixed overhead does not hide the line, because even the 1,000-record median is a few tenths of a millisecond of real loop work rather than an empty call. Divide and conquer is the case where the two metrics part company. The read count grows like n log n. The clock grows only slightly faster than linear, with slope {slope(results, "divide_and_conquer", 10000, 1000000)} from 10,000 to 1,000,000 records, because the Python call overhead is a large linear term beside a small log factor. The ranking the textbook predicts is still the ranking the clock shows. At 10,000 records brute force takes {fmt_ms(window_row(results, "brute_force", 10000)["median_ms"])}, divide and conquer takes {fmt_ms(window_row(results, "divide_and_conquer", 10000)["median_ms"])}, and Kadane takes {fmt_ms(window_row(results, "kadane", 10000)["median_ms"])}. The n² projection puts brute force near {fmt_ms(window_row(results, "brute_force", 1000000)["predicted_median_ms"])} at one million records. That cell was not executed. Kadane's measured median at the same size is {fmt_ms(window_row(results, "kadane", 1000000)["median_ms"])}.</p>
<p>The heap is the disagreement we expected, and it has to be read in two columns. With k = {k}, a late random record rarely beats the current root, so the comparison count on market order at one million records is {fmt_ops(heap_1m["operations"])}, against {fmt_ops(heap_best_1m["operations"])} when the true top K are already first and {fmt_ops(heap_worst_1m["operations"])} when every record is inserted. Random order is the easy case in the comparison model, just as the best-case bound Θ(n + k log k) describes. An engineer who quotes only Θ(n log k) will overestimate this file. An engineer who quotes only the random-order graph will be surprised by an ascending stream, whose median was {fmt_ms(heap_worst_1m["median_ms"])}.</p>
<p>The wall clock does not copy that comparison story at the largest size. The market-order heap took {fmt_ms(heap_1m["median_ms"])}. The prepared best-case layout took {fmt_ms(heap_best_1m["median_ms"])}, slower than market order, even though it performed slightly fewer comparisons. The prepared arrays are permutations of the original objects, so the scan chases pointers instead of walking allocation order. Figure 4 still shows the worst case above the best case, which is the right direction, but it is not a picture of "best case equals fastest clock." The operation count is the picture of the case analysis. Merge sort does not get that split. On the ordered layout the comparison count at one million records is {fmt_ops(sort_best_1m["operations"])}, and on market order it is {fmt_ops(sort_1m["operations"])}. Both stay Θ(n log n). The clocks at that size are {fmt_ms(sort_best_1m["median_ms"])}, {fmt_ms(sort_worst_1m["median_ms"])}, and {fmt_ms(sort_1m["median_ms"])}. The comparison win is real and the clock win has mostly been swallowed by the cost of touching every object. At 1,000 records the clock still shows the run: the ordered sort median is {fmt_ms(top_row(results, "full_sort", "best_for_heap", 1000)["median_ms"])} and the market-order sort median is {fmt_ms(top_row(results, "full_sort", "random", 1000)["median_ms"])}. The required comparison is therefore not the sentence "the heap is faster." On market order the heap is faster at every size we timed. On an already ordered list, merge sort still pays Θ(n log n) comparisons, so it does not become the cheap linear pass a run-detecting sort would be. On the ascending stream the heap pays for a replacement at every index.</p>
<p>Space followed the same split. Kadane's traced peak stays under 500 bytes at every size. Divide and conquer's peak grows from a few kilobytes along the recursion, not with a second copy of the array. Brute force holds an n-word prefix: about 40 KB at 1,000 records and about 400 KB at 10,000. The heap's traced peak stays at about {heap_1m["peak_bytes"]:,} bytes for every size, which is the size-K node storage. The full sort's peak at one million records is about {sort_1m["peak_bytes"] / 1_000_000:.0f} MB, the temporary storage of the sort. None of these space costs is why the quadratic algorithm fails. Time is why it fails. The pair count n(n+1)/2 is why the 1,000,000-record trial stays a projection after the 100,000-record measurement.</p>

<h2>Algorithmic Efficiency versus Computational Hardness</h2>
<p>Efficiency is a property of an algorithm. Hardness is a property of a problem. Brute force for maximum subarray is inefficient. It is correct, it is polynomial, and it is the wrong polynomial. Kadane shows the problem is solvable in linear time, so the problem is in P. No improvement in the constant factor of the double loop, and no rewrite in C, changes the fact that a quadratic algorithm and a linear algorithm are different algorithms for an easy problem. The dashed line on the runtime figure is an efficiency statement: this implementation will not finish a million-record brute-force trial in a class period. It is not a hardness statement. We already have a linear algorithm that does finish.</p>
<p>Hardness shows up when the question changes shape. Cardinality-constrained mean-variance portfolio selection asks for a subset of at most m assets that is optimal for a quadratic utility of expected return and covariance. That problem is NP-hard. The proof idea is the usual one: a polynomial-time solver for every covariance pattern would solve a known NP-complete packing problem. Our Top-K routine does not solve it. Top-K maximizes a linear score with no interaction between the chosen names. The moment the score of a set is not the sum of scores of its members, "keep a heap of size K" is no longer optimal, and for general interactions one should not expect a polynomial algorithm unless P = NP.</p>
<p>The course distinction is easy to lose in a timing table. A group can make brute force look smarter with a faster language and still have an inefficient algorithm. A group can also discover that some neighboring trading question has no Kadane-style rescue. The right response to the first situation is a better algorithm. The right response to the second is an approximation, a heuristic with a stated gap, or a proof that a polynomial algorithm would collapse P and NP. Measuring c·n² more carefully does not cross that line.</p>

<h2>8. CLO reflections</h2>
<h3>A. Asymptotic analysis</h3>
<p>Question. For each algorithm, which of the best, average, and worst cases describes the S&amp;P 500 prefixes, and which algorithm should the tool run?</p>
<p>The change arrays are ordinary market data, not an adversarial pattern, but brute force, divide and conquer, and Kadane do not have a faster best case in our code. Their loops always run. The bound that describes the file is therefore the only bound: Θ(n²), Θ(n log n), and Θ(n). The tool can run all three when n is a few thousand, because the agreement check is worth a second. It should trust Kadane when n grows. The sort-versus-heap choice does depend on the case. Market order plus k = {k} behaves like the heap's easy case. The tool still implements the worst-case algorithm correctly; the benchmark is what tells a reader not to quote only the worst-case expression when they describe this file.</p>
<h3>B. Divide and conquer</h3>
<p>Question. Why is the crossing answer enough to complete the recurrence, and did the clock grow like n log n?</p>
<p>The crossing argument is the whole proof. Without it, the two halves do not determine a window that straddles the midpoint, and induction fails. With it, every optimal window is produced by one of three recursive cases. The Master Theorem then turns the linear combine step into Θ(n log n), with no extra log factors hidden in the combine. The element-read count is the measurement that matches that bound: it grows faster than n and slower than n², from {fmt_ops(window_row(results, "divide_and_conquer", 1000)["operations"])} reads at 1,000 records to {fmt_ops(window_row(results, "divide_and_conquer", 1000000)["operations"])} reads at 1,000,000. The wall-clock slope on the same inputs is lower, {slope(results, "divide_and_conquer", 10000, 1000000)} from 10,000 to 1,000,000 records, because each recursive call allocates a result. We do not paper over that gap. The recurrence explains the reads. The clock explains which algorithm to ship. Kadane's median at one million records is {fmt_ms(window_row(results, "kadane", 1000000)["median_ms"])}, against {fmt_ms(window_row(results, "divide_and_conquer", 1000000)["median_ms"])} for divide and conquer. Divide and conquer remains the algorithm whose proof a reviewer can check from the three-way case split, and it remains in the repository so that check can be made against the code.</p>
<h3>C. Heaps and sorting</h3>
<p>Question. When does the size-K heap beat a full sort, and what do the best and worst inputs do to that claim?</p>
<p>On market order at one million records, the heap's median was {fmt_ms(heap_1m["median_ms"])} with {fmt_ops(heap_1m["operations"])} comparisons, against the sort's {fmt_ms(sort_1m["median_ms"])} and {fmt_ops(sort_1m["operations"])} comparisons. The heap wins that input because k stays {k} while n grows, and because a random late score rarely replaces the root. The worst-case layout removes the comfort in both columns: {fmt_ops(heap_worst_1m["operations"])} comparisons and a median of {fmt_ms(heap_worst_1m["median_ms"])}. The best-case comparison count falls to {fmt_ops(heap_best_1m["operations"])}, which is the Θ(n + k log k) bound in the data. The best-case clock does not fall with it. At one million records that prepared layout took {fmt_ms(heap_best_1m["median_ms"])}, slower than market order, because the objects are no longer in allocation order. Merge sort does not drop to a linear comparison count. Ordered inputs still take {fmt_ops(sort_best_1m["operations"])} comparisons, and the one-million-record clocks stay near the market-order sort. The smaller sizes still show the run in the clock: at 1,000 records the ordered sort takes {fmt_ms(top_row(results, "full_sort", "best_for_heap", 1000)["median_ms"])} and the market-order sort takes {fmt_ms(top_row(results, "full_sort", "random", 1000)["median_ms"])}. The lesson is that the heap is the right structure when k is small and the input is not adversarial, and that a sorted run is a comparison result before it is a runtime result. The implementation keeps both algorithms, and the tests force them to return the same K names, including ties.</p>
<h3>D. Hardness</h3>
<p>Question. This window is solvable in linear time. Which nearby market problem is NP-hard, and why does a faster implementation not move that problem into P?</p>
<p>Maximum subarray is in P because Kadane is a correct linear algorithm. Cardinality-constrained mean-variance optimization is NP-hard because the objective mixes the chosen assets through a covariance matrix; a polynomial algorithm for every such matrix would yield a polynomial algorithm for an NP-complete problem. Writing the quadratic double loop in a faster language multiplies c. It does not produce a polynomial-time portfolio solver, and it does not produce a subquadratic lower bound either. The reflection we owe the course is to say which of those two situations we are in before we celebrate a timing table. In this project the trading window is the first situation. We already replaced the inefficient algorithm. The interacting portfolio is the second situation, and it is not the program we claim to have solved.</p>

<h2>9. Conclusion</h2>
<p>The repository contains a command-line tool, tests, a four-size benchmark with a second metric, and a page that shows the same tables. On the downloaded Kaggle S&amp;P 500 CSV the three window algorithms agree, and the three Top-K algorithms agree. The clocks follow the textbook order whenever the bound is tight and data-independent. They follow the finer best-case and worst-case story for the heap. Merge sort stays Θ(n log n) on every layout. Brute force at a million records is a projection, computed from the measured 100,000-record trial, and the exact pair count n(n+1)/2 is reported beside that projection. The problem those algorithms solve is easy in the complexity sense and still worth an algorithmic choice in the practical sense. Those are different claims, and the measurements support both.</p>

<h2>References</h2>
<p>Cormen, T. H., Leiserson, C. E., Rivest, R. L., and Stein, C. <em>Introduction to Algorithms</em>. MIT Press. Maximum-subarray section and the Master Theorem.</p>
<p>Bentley, J. <em>Programming Pearls</em>. Addison-Wesley. The linear maximum-subarray scan associated with Kadane.</p>
<p>Knuth, D. E. <em>The Art of Computer Programming</em>, Volume 3. Merge sort and the binary heap.</p>
<p>Bienstock, D. Computational study of a family of mixed-integer quadratic programming problems. <em>Mathematical Programming</em> (1996). Cardinality-constrained portfolio optimization is NP-hard.</p>
<p>Saleeby, J. S&amp;P 500 OHLC stock data. Kaggle dataset <code>jacksaleeby/s-and-p500-historical-data</code>, file <code>SP500_Historical_Data.csv</code>. The measurements use that downloaded file.</p>
<p>Kean University. CPS 3440 Analysis of Algorithms. Undergraduate catalog, 2026–2027.</p>
</body>
</html>
"""


def write_qr() -> Path:
    import qrcode

    destination = DOCS / "assets" / "site-qr.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    code.add_data(SITE)
    code.make(fit=True)
    image = code.make_image(fill_color="#14342b", back_color="white")
    image.save(destination)
    return destination


def main() -> None:
    results = load()
    DOCS.mkdir(parents=True, exist_ok=True)
    qr_path = write_qr()
    (DOCS / "index.html").write_text(build_site(results), encoding="utf-8")
    (DOCS / "paper.html").write_text(build_paper(results), encoding="utf-8")
    print(f"wrote {DOCS / 'index.html'}")
    print(f"wrote {DOCS / 'paper.html'}")
    print(f"wrote {qr_path}")


if __name__ == "__main__":
    main()
