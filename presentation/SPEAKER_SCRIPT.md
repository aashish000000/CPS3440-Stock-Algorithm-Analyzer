# Speaker script

CPS 3440 presentation for the Historical Stock Market Algorithm Analyzer.

Pace: about 150 words per minute. The slide lines below are about 1,690 words, which is about 11 minutes. Leave questions until the end. Each slide names the person who speaks. Advance when that person finishes the paragraph for the slide.

The numbers are the medians in `benchmarks/results.json` from the downloaded Kaggle file `SP500_Historical_Data.csv` (472 tickers, 3 January 2000 through 20 February 2026). Brute force at 100,000 and 1,000,000 records is a projection. Do not call those two figures measurements.

## Slide 1 — Title (0:00–0:35) — Aashish Joshi

Hello. We are Aashish Joshi, Aron Dardouri, Bhartendra Kumar Mandal, and Brian Lucero. This is our CPS 3440 project: a historical stock market algorithm analyzer. We took one public S&P 500 file and asked two algorithm questions. What single buy and later sell would have made the most money per share, and which records were the largest movers? I will start with the data and the program. Aron will cover brute force and the benchmark. Bhartendra will cover divide and conquer, and the line between a slow algorithm and a hard problem. Brian will cover sorting and the heap.

## Slide 2 — Two questions (0:35–1:25) — Aashish Joshi

The first question is the maximum-subarray problem. Take adjusted closes, replace them with daily changes, and find the contiguous block with the largest sum. That sum is the profit per share of buying at the start of the block and selling at the end. If every block loses money, the right action is to stay out. When two windows tie, we keep the earlier one, so the three algorithms can be checked against each other exactly.

The second question is Top-K. Rank records by a score, break ties by name, and keep K of them. On Apple, every window algorithm returns the same trade: buy on 8 October 2002 at 20 cents and sell on 2 December 2025 at $285.92, a profit of $285.72 per share. Across 472 stocks, NVIDIA has the largest buy-and-hold return, 210,811 percent.

## Slide 3 — The file (1:25–2:20) — Aashish Joshi

The measurements use the downloaded Kaggle CSV, `SP500_Historical_Data.csv`, from the dataset `jacksaleeby/s-and-p500-historical-data`. The columns are ticker, date, open, high, low, close, adjusted close, and volume. The file has 2,703,531 rows, 472 tickers, and dates from 3 January 2000 through 20 February 2026. It is gitignored because it is about 143 megabytes.

Adjusted close is an integer number of micro-dollars, so the algorithms compare identical integers. Those prices become 2,703,059 daily changes. The scaling study uses prefixes of 1,000, 10,000, 100,000, and 1,000,000 records. The tool reads this file by default. The Yahoo `--fetch` path was not used for these numbers.

## Slide 4 — The tool (2:20–3:05) — Aashish Joshi

`prices.py` loads the CSV and turns closes into changes. `max_subarray.py` runs brute force, divide and conquer, and Kadane on one ticker. `top_k.py` ranks the whole universe with a full sort, a size-K heap, and quickselect. The command line prints both answers and says whether the algorithms agree.

On this file they do agree: one Apple window, and the same top ten movers. The unit tests cover the CLRS example, an all-negative array, equal windows, and ties on the ticker. I will hand the quadratic algorithm and the timer to Aron.

## Slide 5 — Brute force (3:05–3:55) — Aron Dardouri

Brute force builds a prefix array and then scores every start and end with one subtraction. Every nonempty window is considered once, so the best pair is the best window under our earliest-window rule. The loops do not look at the values to decide whether to stop. Best, average, and worst time are the same bound, theta of n squared. The extra memory is the prefix, theta of n.

Five trials, same prefix, median. At 1,000 records the median is 60.2 milliseconds. At 10,000 records it is 17.65 seconds. The log-log slope on that decade is 2.47, beside the model value of 2. The pair count is exactly n times n plus one, over two.

## Slide 6 — Timed and projected (3:55–4:45) — Aron Dardouri

The benchmark has two columns on purpose. The first is the median wall-clock time. The second is an operation count: pair iterations, element reads, or comparisons. Brute force is executed only through 10,000 records. One trial there already takes 17.65 seconds, and the next sizes are 100 times and 10,000 times as many pairs.

We fit c from that 10,000-record median and project c n squared. At 100,000 records the projection is 29.4 minutes. At 1,000,000 records it is 49.0 hours. Those two cells were not timed. The figure draws them dashed, and the tables say projected. The pair count at those sizes is still exact.

## Slide 7 — Window results (4:45–5:40) — Aron Dardouri

Here is the comparison at 10,000 changes. Brute force, 17.65 seconds. Divide and conquer, 15.6 milliseconds. Kadane, 4.4 milliseconds. The quadratic algorithm is about 4,000 times the linear scan at a size that still fits in a class period. At one million changes, Kadane's measured median is 451 milliseconds. The brute-force cell beside it is the 49 hour projection, and we did not run it.

Solid marks were timed for five trials. The dashed segment is brute force past 10,000 only. Kadane and divide and conquer were timed at all four sizes. I will pass the recurrence to Bhartendra.

## Slide 8 — Divide and conquer (5:40–6:40) — Bhartendra Kumar Mandal

Divide and conquer splits the array at the midpoint. An optimal window is entirely on the left, entirely on the right, or it crosses the midpoint. The first two cases are the recursive calls. The crossing case is the one that makes the proof work: a crossing window must be a suffix of the left half plus a prefix of the right half, and both of those are a linear scan. Ties keep the earlier index, the same rule the other two algorithms use.

The recurrence is T of n equals 2 T of n over 2, plus theta of n. The Master Theorem gives theta of n log n. Every input pays the same scans, so best, average, and worst time agree. The extra space is the recursion stack, theta of log n. At one million records a dry recursion, which does not read the prices, counts 20,951,424 element reads. The measured median on the real prefix is 1.77 seconds.

## Slide 9 — The clock and the recurrence (6:40–7:30) — Bhartendra Kumar Mandal

Kadane is the one-pass scan. A negative running sum is thrown away, because extending it cannot help a later day. The loop is theta of n in every case and uses a constant amount of extra memory. Any correct algorithm has to read every entry, so the linear bound is tight for the problem.

On this file Kadane's wall-clock slope from 1,000 to 1,000,000 records is 1.00, and the million-record median is 451 milliseconds. Divide and conquer's reads grow like n log n. Its wall-clock slope from 10,000 to 1,000,000 is 1.03, because each Python call allocates a result. The reads follow the theorem. The clock says which algorithm to ship: Kadane at 451 milliseconds, against 1.77 seconds for divide and conquer. Where we also ran brute force, all three answers match.

## Slide 10 — Sort versus heap (7:30–8:25) — Brian Lucero

Top-K uses one total order: higher score first, and the earlier ticker on a tie. The full sort and the heap both implement that order, and the tests require them to return the same names. Python's sort is Timsort. It is linear on one long run, and n log n on average and in the worst case, with linear extra space. The heap keeps at most K survivors, with the weakest at the root. Its worst case is n log k, when every record enters. Its best case is n plus k log k, when the first K records are already the answer. The extra space is K nodes. In the study, K is 10.

On market order at one million daily moves, the sort median is 596 milliseconds and 13.7 million comparisons. The heap median is 177 milliseconds and 1,000,374 comparisons. On this ordinary input the heap does about one comparison per record, and it is the faster algorithm.

## Slide 11 — Cases (8:25–9:25) — Brian Lucero

The case split is in the comparison column. At one million records the best-case heap makes 1,000,009 comparisons, market order makes 1,000,374, and the worst case, where every arrival is inserted, makes 4,399,965. The clocks are 521 milliseconds for the prepared best case, 177 milliseconds for market order, and 894 milliseconds for the worst case. The prepared best-case array is a permutation of the Python objects, so the scan loses allocation-order locality. That is why the best-case clock is slower than market order even though it does slightly less comparing. The bars still put the worst case above the best case at every size. The comparison count is the picture of theta of n versus theta of n log k.

Timsort has the matching split. On a fully ordered layout the comparison count falls to n minus 1. At one million records the clock stays near the market-order sort, about 610 to 670 milliseconds against 596. At 1,000 records the ordered sort is 0.068 milliseconds and the market-order sort is 0.190. The heap wins the file we have. A sorted run shows up in the comparison count before it shows up as a large change in the clock.

## Slide 12 — Efficiency and hardness (9:25–10:20) — Bhartendra Kumar Mandal

This is the distinction the course asks us to keep straight. Efficiency belongs to an algorithm. Hardness belongs to a problem. Brute force for the trading window is correct, and it is polynomial, and it is the wrong polynomial. Kadane shows the problem is in P. The dashed line is an efficiency statement: this interpreter projects 49 hours for one million records, and we did not start that trial. It is not a hardness statement. We already have a linear algorithm that finishes the same input in 451 milliseconds.

Hardness shows up when the question changes shape. Cardinality-constrained mean-variance portfolio selection asks for a subset of assets that is optimal for a quadratic utility of return and covariance. That problem is NP-hard, because the chosen names interact. Our Top-K routine does not solve it. A heap of size K is the right tool when the score of a set is the sum of the scores of its members. A faster language multiplies the constant on the double loop. It does not move the portfolio problem into P. The reflections in the paper, labeled A through D, walk through asymptotic cases, the crossing argument, the heap against the sort, and this hardness line.

## Slide 13 — Close (10:20–11:05) — Aashish Joshi

The site on the screen is the GitHub Pages directory in the repository. It has the same tables and the four figures. Brute force at 100,000 and one million records is labeled projected there, in the paper, and on Aron's slide. The paper is ten pages. The QR code opens that site. The speaker notes match this script, and `CONTRIBUTIONS.md` has two resume lines for each of us, tied to these measurements. Thank you. We can take questions on the file, the projection, the recurrence, or the heap.
