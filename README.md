# Historical Stock Market Algorithm Analyzer

CPS 3440 group project at Kean University. The program finds the best single buy and later sell in a price series, and the top movers in a universe, with several algorithms whose costs are far apart. Every published timing was run on the downloaded Kaggle S&P 500 file.

Team: Aashish Joshi, Aron Dardouri, Bhartendra Kumar Mandal, and Brian Lucero.

Site: https://aashish000000.github.io/CPS3440-Stock-Algorithm-Analyzer/

## Layout

| Path | What it is |
| --- | --- |
| `analyzer/` | The library and the command-line tool. Standard library only. |
| `benchmarks/results.json` | Five-trial medians, operation counts, and the brute-force projection. |
| `docs/` | GitHub Pages: the site, the paper, the PDF, and the figures. |
| `docs/algorithms.md` | Pseudocode, correctness, and best, average, and worst bounds. |
| `presentation/` | The slide deck and the timed speaker script. |
| `tests/` | Unit tests, including the CLRS maximum-subarray example. |
| `CONTRIBUTIONS.md` | Responsibilities and two resume bullets per person. |
| `data/SP500_Historical_Data.csv` | The Kaggle download. Gitignored. About 143 MB. |

## Algorithms

Daily adjusted-close changes are integers in micro-dollars. The sum of a contiguous block is the profit per share of one buy and one later sell. Ties keep the earliest window.

| Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- |
| Brute force | Θ(n²) | Θ(n²) | Θ(n²) | Θ(n) |
| Divide and conquer | Θ(n log n) | Θ(n log n) | Θ(n log n) | Θ(log n) |
| Kadane | Θ(n) | Θ(n) | Θ(n) | Θ(1) |

Top-K uses the order (higher score, then earlier ticker). The scaling study uses k = 10.

| Algorithm | Best | Average | Worst | Extra space |
| --- | --- | --- | --- | --- |
| Full sort (Timsort) | Θ(n) | Θ(n log n) | Θ(n log n) | Θ(n) |
| Binary heap of size K | Θ(n + k log k) | Θ(n log k) bound | Θ(n log k) | Θ(k) |
| Quickselect | Θ(n) | Θ(n) | Θ(n²) | Θ(log n) |

Quickselect is in the tool and the tests. The benchmark tables compare the sort with the heap.

## Requirements

The analyzer and the tests need Python 3.12 and the standard library.

```bash
python3 -m pip install -r requirements.txt
```

`requirements.txt` covers matplotlib (the figures), qrcode and pillow (the site QR code), and python-pptx (the slides).

## Run the analyzer

Place the Kaggle export at `data/SP500_Historical_Data.csv`. The original dataset is [jacksaleeby/s-and-p500-historical-data](https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data). Columns are `Ticker`, `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, and `Volume`. This download has 2,703,531 rows, 472 tickers, and dates from 2000-01-03 through 2026-02-20.

```bash
python3 -m analyzer --ticker AAPL --k 10
python3 -m analyzer --ticker AAPL --k 10 --html docs/results.html
python3 -m unittest discover -s tests
```

On that file the three window algorithms agree: buy AAPL on 2002-10-08 at $0.20 and sell on 2025-12-02 at $285.92, profit $285.72 per share. Sort, heap, and quickselect agree on the top 10 buy-and-hold returns, led by NVDA at 210,811.11%.

`--since` and `--until` take `YYYY-MM-DD`. `--fetch PATH` downloads a Yahoo Finance history and was not used for the paper or the benchmark. The offline sample is `tests/fixtures/sample.csv`.

## Benchmark

```bash
python3 -m analyzer.benchmark --data data/SP500_Historical_Data.csv --out benchmarks/results.json --figures docs/assets
python3 docs/render.py
```

The timer uses prefixes of 1,000, 10,000, 100,000, and 1,000,000 records, five trials, and the median. A second column counts pair iterations, element reads, or comparisons.

Brute force is executed only through 10,000 records (median 17.65 s). The 100,000-record and 1,000,000-record brute-force times are the n² projection from that median: 29.4 minutes and 49.0 hours. They are labeled projected. They were not measured. Kadane's measured median at 1,000,000 records is 451 ms. Divide and conquer's is 1.77 s. On market order at 1,000,000 daily moves, the size-10 heap median is 177 ms and the full sort median is 596 ms.

`docs/render.py` rebuilds `docs/index.html` and `docs/paper.html` from `benchmarks/results.json`, and writes `docs/assets/site-qr.png`.

## Paper, slides, and site

GitHub Pages serves the `docs/` directory. The technical paper is `docs/paper.html` and `docs/paper.pdf` (10 pages). It includes the section **Algorithmic Efficiency versus Computational Hardness**, a theory-versus-observed discussion, and CLO reflections A through D.

Regenerate the PDF from the repository root:

```bash
google-chrome --headless --disable-gpu --no-sandbox \
  --user-data-dir=/tmp/chrome-paper \
  --no-pdf-header-footer \
  --print-to-pdf=docs/paper.pdf \
  file://$PWD/docs/paper.html
```

The deck is `presentation/CPS3440-Stock-Algorithm-Analyzer.pptx`. Rebuild it with `python3 presentation/build_slides.py`. The timed script is `presentation/SPEAKER_SCRIPT.md` (about 11 minutes at 150 words per minute). One slide carries the QR code for the site.

Resume lines grounded in these measurements are in `CONTRIBUTIONS.md`.
