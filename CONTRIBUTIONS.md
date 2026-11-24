# Contributions

CPS 3440, Kean University. DRAFT: each person must check and edit their own section so it lists only what they personally wrote and pushed. GitHub history (commits and pull requests) must match these statements. The resume bullets use real numbers from `benchmarks/results.json` (one MacBook, five trials, median); rewrite them in your own words and keep only what is true of your own work.

AI assistance: parts of this project (code, benchmarks, paper, slides, and this repository's layout) were developed with help from Claude, an AI assistant. Each team member is responsible for understanding and explaining the portion listed under their name.

## Aashish Joshi — brute force (baseline)

Responsibilities: the brute-force maximum-subarray algorithm in `analyzer/max_subarray.py` and its tests.

Resume bullets (draft):
- Implemented a Θ(n²) brute-force baseline for the best-buy/best-sell problem in Python and benchmarked it against Θ(n log n) and Θ(n) algorithms on 2.7 million rows of S&P 500 data.
- Measured 12.7 s at 10,000 records against 2.9 ms for a linear scan (about 4,400 times slower), fitted a log-log slope of 2.50 against the model value of 2, and projected 21 minutes at 100,000 and 35 hours at 1,000,000 records, labelled as projections and not measurements.

## Bhartendra Kumar Mandal — divide and conquer

Responsibilities: the divide-and-conquer maximum-subarray algorithm in `analyzer/max_subarray.py` (the crossing scan and the earliest-window tie rule) and its tests.

Resume bullets (draft):
- Implemented the CLRS divide-and-conquer maximum-subarray algorithm, solved its recurrence T(n) = 2T(n/2) + Θ(n) with the Master Theorem, and checked it against the brute-force and Kadane implementations on the CLRS example and on real data.
- Verified the Θ(n log n) bound with an exact operation count (20,951,424 element reads at one million records) and measured 1.28 s at that size with a wall-clock slope of 1.04.

## Aron Dardouri — Kadane's algorithm

Responsibilities: Kadane's one-pass maximum-subarray algorithm in `analyzer/max_subarray.py` and its tests.

Resume bullets (draft):
- Implemented Kadane's Θ(n) time, Θ(1) space algorithm for the best single buy and sell on 26 years of S&P 500 data, and showed it agrees with the brute-force and divide-and-conquer answers on every tested input.
- Measured 311 ms at one million records with a log-log slope of 1.01 across 1,000 to 1,000,000 records, about four times faster than divide and conquer, and used the result to recommend Kadane as the algorithm to ship.

## Still to fill in (who did what)

These parts of the repository are not yet assigned to a named person. Add each to the right section above once you agree who wrote it and the commits show it: `analyzer/prices.py`, `analyzer/__main__.py` and `analyzer/report.py` (data loading and the command-line tool), `analyzer/top_k.py` (merge sort, binary heap, quickselect, and the Top-K tests), `analyzer/benchmark.py` (timing harness and figures), the GitHub Pages site, the paper, the slides, and the Colab notebook.

## Notes

- Brute force at 100,000 and 1,000,000 records is an n² projection from the 10,000-record median, not a measurement.
- Timings vary by machine and by run, especially the million-record sort. Re-run the benchmark before quoting them.
