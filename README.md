# CPS3440 Stock Algorithm Analyzer

CPS 3440 group project: comparing max-subarray and Top-K algorithms on real S&P 500 data.

Website: https://aashish000000.github.io/CPS3440-Stock-Algorithm-Analyzer/

## Algorithms

The best buy/sell window is the maximum subarray of daily adjusted-close changes. The sum of that block is the profit per share of buying at the start and selling at the end.

| Algorithm | Complexity |
| --- | --- |
| Brute force | O(n^2) |
| Divide and conquer | O(n log n) |
| Kadane's scan | O(n) |

Top movers ranks stocks by buy-and-hold return.

| Algorithm | Complexity |
| --- | --- |
| Full sort | O(n log n) |
| Binary heap of size K | O(n log k) |
| Quickselect | O(n) average |

Each group is checked against the others. On ties, the earliest window wins, and equal returns are ordered by ticker.

## Run

Python 3.12 from the standard library is enough. The measurements were run on the downloaded [Kaggle S&P 500 OHLC file](https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data). The original filename is `SP500_Historical_Data.csv`. Columns are `Ticker`, `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, and `Volume`. The download has 2,703,531 rows, 472 tickers, and dates from 2000-01-03 through 2026-02-20. It is gitignored at `data/SP500_Historical_Data.csv` (about 143 MB).

```bash
python3 -m analyzer --ticker AAPL --k 10 --html docs/results.html
python3 -m analyzer.benchmark
```

Both commands read that Kaggle CSV by default. `--fetch PATH` is an optional Yahoo Finance fallback. It writes a different, shorter history and is not a substitute for the Kaggle file.

```bash
python3 -m analyzer data/SP500_Historical_Data.csv --ticker AAPL --k 10
```

`--since` and `--until` take `YYYY-MM-DD`. The offline sample is `tests/fixtures/sample.csv`.

```bash
python3 -m unittest discover -s tests
```
