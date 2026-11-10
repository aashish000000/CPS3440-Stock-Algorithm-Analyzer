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

Python 3.12 from the standard library is enough. Download current S&P 500 history from Yahoo Finance (the same adjusted OHLCV series as the [Kaggle S&P 500 dataset](https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data)) and compare the algorithms:

```bash
python3 -m analyzer --fetch data/SP500_Historical_Data.csv --ticker AAPL --k 10 --html docs/results.html
```

A Kaggle export with `Ticker`, `Date`, and `Adj Close` columns works the same way:

```bash
python3 -m analyzer data/SP500_Historical_Data.csv --ticker AAPL --k 10
```

`--since` and `--until` take `YYYY-MM-DD`. Symbols Yahoo Finance rejects are skipped and listed on stderr. The offline sample is `tests/fixtures/sample.csv`.

```bash
python3 -m unittest discover -s tests
```
