# Contributions

CPS 3440, Kean University. DRAFT: each person must check and edit their own section so it lists only what they personally wrote and pushed. GitHub history (commits and pull requests) must match these statements. The resume bullets use real numbers from `benchmarks/results.json` (one MacBook, five trials, median); rewrite them in your own words and keep only what is true of your own work.

AI assistance: parts of this project (code, benchmarks, paper, slides, and this repository's layout) were developed with help from Claude, an AI assistant. Each team member is responsible for understanding and explaining the portion listed under their name.

## Aashish Joshi — brute force (baseline)

Responsibilities: the brute-force maximum-subarray algorithm in `analyzer/max_subarray.py` and its tests.

Also owns (can explain and defend): the data loading and command-line tool (`analyzer/prices.py`, `analyzer/__main__.py`, `analyzer/report.py` and `tests/test_prices.py`), the repository layout and README, and the GitHub Pages site.

Resume bullets (draft):
- Implemented a Θ(n²) brute-force baseline for the best-buy/best-sell problem in Python and benchmarked it against Θ(n log n) and Θ(n) algorithms on 2.7 million rows of S&P 500 data.
- Measured 12.7 s at 10,000 records against 2.9 ms for a linear scan (about 4,400 times slower), fitted a log-log slope of 2.50 against the model value of 2, and projected 21 minutes at 100,000 and 35 hours at 1,000,000 records, labelled as projections and not measurements.

## Bhartendra Kumar Mandal — divide and conquer

Responsibilities: the divide-and-conquer maximum-subarray algorithm in `analyzer/max_subarray.py` (the crossing scan and the earliest-window tie rule) and its tests.

Also owns (can explain and defend): the benchmark runner and figures (`analyzer/benchmark.py`, `tests/test_benchmark.py`, `benchmarks/results.json`), and the technical paper including the CLO reflections.

Resume bullets (draft):
- Implemented the CLRS divide-and-conquer maximum-subarray algorithm, solved its recurrence T(n) = 2T(n/2) + Θ(n) with the Master Theorem, and checked it against the brute-force and Kadane implementations on the CLRS example and on real data.
- Verified the Θ(n log n) bound with an exact operation count (20,951,424 element reads at one million records) and measured 1.28 s at that size with a wall-clock slope of 1.04.

## Aron Dardouri — Kadane's algorithm

Responsibilities: Kadane's one-pass maximum-subarray algorithm in `analyzer/max_subarray.py` and its tests.

Also owns (can explain and defend): the Top-K code in `analyzer/top_k.py` (merge sort, binary heap, quickselect) and `tests/test_top_k.py`. Top-K was originally planned for Brian Lucero, who left the project, so ownership moved to Aron.

Resume bullets (draft):
- Implemented Kadane's Θ(n) time, Θ(1) space algorithm for the best single buy and sell on 26 years of S&P 500 data, and showed it agrees with the brute-force and divide-and-conquer answers on every tested input.
- Measured 311 ms at one million records with a log-log slope of 1.01 across 1,000 to 1,000,000 records, about four times faster than divide and conquer, and used the result to recommend Kadane as the algorithm to ship.

## Shared work

The slides, speaker script, and Colab notebook are shared. Each slide names its speaker, and each person presents the part listed under their name. After Brian Lucero left, ownership of the remaining files was divided as listed above. Check each file's commits and correct this document if any line does not match who actually wrote it.

## Notes

- Brute force at 100,000 and 1,000,000 records is an n² projection from the 10,000-record median, not a measurement.
- Timings vary by machine and by run, especially the million-record sort. Re-run the benchmark before quoting them.
