# Contributions

CPS 3440, Kean University. The measurements below are in `results/results.json`, run on the downloaded Kaggle file `SP500_Historical_Data.csv` (472 tickers, 3 January 2000 through 20 February 2026, 2,703,059 daily changes). Brute force is timed through 100,000 records, once at that size. The 1,000,000-record brute-force runtime is the n² projection from that measurement.

## Aashish Joshi

Responsibilities: `prices.py`, the command-line tool, and the dataset path. Adjusted closes are integer micro-dollars. `python3 -m analyzer` reads the Kaggle CSV by default and reports whether the window algorithms and the Top-K algorithms agree.

Resume bullets:

- Built a Python loader and CLI for the Kaggle S&P 500 history (2.70 million rows, 472 tickers, 2000–2026) that represents adjusted closes as integer micro-dollars and checks three maximum-subarray algorithms against one another.
- Reproduced one Apple buy/sell window across brute force, divide and conquer, and Kadane: buy 2002-10-08 at $0.20, sell 2025-12-02 at $285.92, profit $285.72 per share, and the same top-10 ranking led by NVDA at 210,811%.

## Aron Dardouri

Responsibilities: the Θ(n²) brute-force maximum subarray and `benchmark.py`. The harness runs five trials at 1,000, 10,000, 100,000, and 1,000,000 records, records an operation count beside the median, and stops brute-force timing at 10,000 records.

Resume bullets:

- Implemented prefix-sum brute force for the maximum subarray and a five-trial benchmark; at 10,000 S&P 500 changes the median was 17.65 s, about 4,000× Kadane's 4.415 ms, with a measured log-log slope of 2.47.
- Timed brute force through 100,000 S&P 500 changes, once at that size (33.5 minutes), and kept the 1,000,000-record runtime as a labeled n² projection (55.8 hours) with the exact pair count n(n+1)/2, including 5.000×10¹¹ pairs at n = 1,000,000.

## Bhartendra Kumar Mandal

Responsibilities: divide and conquer in `max_subarray.py`. The crossing scan, the earliest-window tie rule, and the recurrence T(n) = 2T(n/2) + Θ(n). The paper's comparison of that bound with the measured clock, and the section on efficiency versus NP-hardness, are part of this work.

Resume bullets:

- Implemented the CLRS divide-and-conquer maximum subarray, including the crossing suffix-plus-prefix scan; on 1,000,000 market changes the median was 1.77 s and a value-independent dry run counted 20,951,424 element reads.
- Showed that those reads follow Θ(n log n) while the Python wall-clock slope from 10,000 to 1,000,000 records was 1.03, and that Kadane's measured median at the same size was 451 ms against a 49-hour brute-force projection that was not executed.

## Brian Lucero

Responsibilities: `top_k.py`. Full sort and the size-K binary heap share one total order (higher score, then earlier ticker). The benchmark times both on market order, on a best-case layout, and on a worst-case layout, and counts comparisons.

Resume bullets:

- Implemented Top-K with merge sort and a hand-written size-10 min-heap (`push`, `replace_root`, `sift_down`), and added quickselect to the benchmark; the three methods return the same names, including ties.
- Separated heap cases at that size: 1,000,009 comparisons when the top 10 come first, 4,399,965 when every record is inserted (median 894 ms), and documented that the prepared best-case clock (521 ms) is slower than market order because the objects are no longer in allocation order.
