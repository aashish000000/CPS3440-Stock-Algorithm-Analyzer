# Speaker script

CPS 3440 presentation for the Historical Stock Market Algorithm Analyzer.

Pace: about 150 words per minute. The slide lines below are about 1,690 words, which is about 11 minutes. Leave questions until the end. Each slide names the person who speaks. Advance when that person finishes the paragraph for the slide.

The numbers are in `results/results.json` from the downloaded Kaggle file `SP500_Historical_Data.csv` (472 tickers, 3 January 2000 through 20 February 2026). Brute force at 100,000 records is one measured trial. Brute force at 1,000,000 records is a projection. Do not call that cell a measurement.

## Slide 1 — Title (0:00–0:35) — Aashish Joshi

Hello. We are Aashish Joshi, Aron Dardouri, Bhartendra Kumar Mandal, and Brian Lucero. This is our CPS 3440 project: a historical stock market algorithm analyzer. We took one public S&P 500 file and asked two algorithm questions. What single buy and later sell would have made the most money per share, and which records were the largest movers? I will start with the data and the program. Aron will cover brute force and the benchmark. Bhartendra will cover divide and conquer, and the line between a slow algorithm and a hard problem. Brian will cover sorting and the heap.

## Slide 2 — Two questions (0:35–1:25) — Aashish Joshi

The first question is the maximum-subarray problem. Take adjusted closes, replace them with daily changes, and find the contiguous block with the largest sum. That sum is the profit per share of buying at the start of the block and selling at the end. If every block loses money, the right action is to stay out. When two windows tie, we keep the earlier one, so the three algorithms can be checked against each other exactly.

The second question is Top-K. Rank records by a score, break ties by name, and keep K of them. On Apple, every window algorithm returns the same trade: buy on 8 October 2002 at 20 cents and sell on 2 December 2025 at $285.92, a profit of $285.72 per share. Across 472 stocks, NVIDIA has the largest buy-and-hold return, 210,811 percent.

## Slide 3 — The file (1:25–2:20) — Aashish Joshi

The measurements use the downloaded Kaggle CSV, `SP500_Historical_Data.csv`, from the dataset `jacksaleeby/s-and-p500-historical-data`. The columns are ticker, date, open, high, low, close, adjusted close, and volume. The file has 2,703,531 rows, 472 tickers, and dates from 3 January 2000 through 20 February 2026. It is gitignored because it is about 143 megabytes.

Adjusted close is an integer number of micro-dollars, so the algorithms compare identical integers. Those prices become 2,703,059 daily changes. The scaling study uses prefixes of 1,000, 10,000, 100,000, and 1,000,000 records. The tool reads this file by default. The download steps are in `data/README.md`.

## Slide 4 — The tool (2:20–3:05) — Aashish Joshi

`prices.py` loads the CSV and turns closes into changes. `max_subarray.py` runs brute force, divide and conquer, and Kadane on one ticker. `top_k.py` ranks the whole universe with a full sort, a size-K heap, and quickselect. The command line prints both answers and says whether the algorithms agree.

On this file they do agree: one Apple window, and the same top ten movers. The unit tests cover the CLRS example, an all-negative array, equal windows, and ties on the ticker. I will hand the quadratic algorithm and the timer to Aron.

## Slide 5 — Brute force (3:05–3:55) — Aron Dardouri

Brute force builds a prefix array and then scores every start and end with one subtraction. Every nonempty window is considered once, so the best pair is the best window under our earliest-window rule. The loops do not look at the values to decide whether to stop. Best, average, and worst time are the same bound, theta of n squared. The extra memory is the prefix, theta of n.

Five trials, same prefix, median. At 1,000 records the median is 51.3 milliseconds. At 10,000 records it is 17.67 seconds. The log-log slope on that decade is 2.54, beside the model value of 2. From 10,000 to the measured 100,000-record trial the slope is 2.06. The pair count is exactly n times n plus one, over two.

## Slide 6 — Timed and projected (3:55–4:45) — Aron Dardouri

The benchmark has two columns on purpose. The first is wall-clock time. Through 10,000 records that is the median of five trials. Brute force at 100,000 records is one trial, because five of them would be hours. The second column is an operation count: pair iterations, element reads, or comparisons.

The 100,000-record trial measured 33.5 minutes. We fit c from that trial and project c n squared only for 1,000,000 records, which comes out to 55.8 hours. That cell was not timed. The figure draws it dashed, and the table says projected. The pair count at every size is still exact. On the market prefix the time per pair rises from 103 nanoseconds at 1,000 records to 353 at 10,000 and 402 at 100,000. A positive window does extra work, and the longer prefix also leaves cache. Zero-mean random integers stay near 324 and 404 nanoseconds per pair, so a zero mean does not remove the cost.

## Slide 7 — Window results (4:45–5:40) — Aron Dardouri

Here is the comparison at 10,000 changes. Brute force, 17.67 seconds. Divide and conquer, 13.8 milliseconds. Kadane, 3.9 milliseconds. The quadratic algorithm is about 4,500 times the linear scan at a size that still fits in a class period. At 100,000 changes the measured brute-force trial is 33.5 minutes. At one million changes, Kadane's measured median is 497 milliseconds. The brute-force cell beside it is the 55.8 hour projection, and we did not run it.

Solid marks were timed. The dashed segment is only the 1,000,000-record brute-force projection. Kadane and divide and conquer were timed at all four sizes, and brute force was timed through 100,000. I will pass the recurrence to Bhartendra.

## Slide 8 — Divide and conquer (5:40–6:40) — Bhartendra Kumar Mandal

Divide and conquer splits the array at the midpoint. An optimal window is entirely on the left, entirely on the right, or it crosses the midpoint. The first two cases are the recursive calls. The crossing case is the one that makes the proof work: a crossing window must be a suffix of the left half plus a prefix of the right half, and both of those are a linear scan. Ties keep the earlier index, the same rule the other two algorithms use.

The recurrence is T of n equals 2 T of n over 2, plus theta of n. The Master Theorem gives theta of n log n. Every input pays the same scans, so best, average, and worst time agree. The extra space is the recursion stack, theta of log n. At one million records a dry recursion, which does not read the prices, counts 20,951,424 element reads. The measured median on the real prefix is 2.04 seconds.

## Slide 9 — The clock and the recurrence (6:40–7:30) — Bhartendra Kumar Mandal

Kadane is the one-pass scan. A negative running sum is thrown away, because extending it cannot help a later day. The loop is theta of n in every case and uses a constant amount of extra memory. Any correct algorithm has to read every entry, so the linear bound is tight for the problem.

On this file Kadane's wall-clock slope from 1,000 to 1,000,000 records is 1.04, and the million-record median is 497 milliseconds. Divide and conquer's reads grow like n log n. Its wall-clock slope from 10,000 to 1,000,000 is 1.08, because each Python call allocates a result. The reads follow the theorem. The clock says which algorithm to ship: Kadane at 497 milliseconds, against 2.04 seconds for divide and conquer. Where we also ran brute force, all three answers match.

## Slide 10 — Sort versus heap (7:30–8:25) — Brian Lucero

Top-K uses one total order: higher score first, and the earlier ticker on a tie. Merge sort, the heap, and quickselect all implement that order, and the tests require them to return the same names. Merge sort is n log n in every case, including a sorted run, with linear extra space. The heap keeps at most K survivors, with the weakest at the root. Its worst case is n log k, when every record enters. Its best case is n plus k log k, when the first K records are already the answer. The extra space is K nodes. Quickselect is average linear and worst-case quadratic, then a merge sort of the K survivors. In the study, K is 10.

On market order at one million daily moves, merge sort's median is 5.41 seconds and 18.6 million comparisons. The heap median is 115 milliseconds and 1,000,383 comparisons. Quickselect's median is 340 milliseconds. On this ordinary input the heap does about one comparison per record, and it is the faster algorithm. Merge sort pays n log n in Python, so its clock is the slow one.

## Slide 11 — Cases (8:25–9:25) — Brian Lucero

The case split is in the comparison column. At one million records the best-case heap makes 1,000,009 comparisons, market order makes 1,000,383, and the worst case, where every arrival is inserted, makes 6,066,615. The clocks are 307 milliseconds for the prepared best case, 115 milliseconds for market order, and 1.14 seconds for the worst case. The prepared best-case array is a permutation of the Python objects, so the scan loses allocation-order locality. That is why the best-case clock is slower than market order even though it does slightly less comparing. The bars still put the worst case above the best case at every size. The comparison count is the picture of theta of n versus theta of n log k.

Merge sort does not get a linear comparison count on a sorted run. The case split that the bars show is the heap: about n comparisons when the top K come first, and several times that when every record is inserted. The heap wins the market-order file we have. A sorted run is not a license to quote a linear sort.

## Slide 12 — Efficiency and hardness (9:25–10:20) — Bhartendra Kumar Mandal

This is the distinction the course asks us to keep straight. Efficiency belongs to an algorithm. Hardness belongs to a problem. Brute force for the trading window is correct, and it is polynomial, and it is the wrong polynomial. Kadane shows the problem is in P. The dashed line is an efficiency statement: this interpreter projects 55.8 hours for one million records, and we did not start that trial. It is not a hardness statement. We already have a linear algorithm that finishes the same input in 497 milliseconds.

Hardness shows up when the question changes shape. Cardinality-constrained mean-variance portfolio selection asks for a subset of assets that is optimal for a quadratic utility of return and covariance. That problem is NP-hard, because the chosen names interact. Our Top-K routine does not solve it. A heap of size K is the right tool when the score of a set is the sum of the scores of its members. A faster language multiplies the constant on the double loop. It does not move the portfolio problem into P. The reflections in the paper, labeled A through D, walk through asymptotic cases, the crossing argument, the heap against the sort, and this hardness line.

## Slide 13 — Close (10:20–11:05) — Aashish Joshi

The site on the screen is the GitHub Pages directory in the repository. It has the same tables and the four figures. Brute force at one million records is labeled projected there, in the paper, and on Aron's slide. The 100,000-record brute-force cell was measured. The paper is ten pages. The QR code opens that site. The speaker notes match this script, and `CONTRIBUTIONS.md` has two resume lines for each of us, tied to these measurements. Thank you. We can take questions on the file, the projection, the recurrence, or the heap.
