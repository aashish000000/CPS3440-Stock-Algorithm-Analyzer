# Algorithms

Two problems are solved on the Kaggle-style S&P 500 file. Daily adjusted-close changes are integers in micro-dollars. A contiguous sum is the profit of one buy and one later sell. Top-K ranks records by an integer score, then by name.

An empty maximum subarray means every window loses money, so the best action is to stay out. Ties keep the earliest window. Top-K ties keep the alphabetically earlier name. Those rules are why the implementations can be checked against each other exactly.

## 1. Brute-force maximum subarray

### Pseudocode

```
function BRUTE-FORCE(A[0..n-1]):
    best ← 0
    best window ← none
    prefix[0] ← 0
    for i ← 0 to n-1:
        prefix[i+1] ← prefix[i] + A[i]
    for start ← 0 to n-1:
        for end ← start to n-1:
            total ← prefix[end+1] − prefix[start]
            if total > best, or (total = best > 0 and this window starts earlier):
                best ← total
                record [start, end]
    return best window
```

### Correctness

`prefix[end+1] − prefix[start]` equals `A[start] + … + A[end]` by induction on the prefix recurrence. Every nonempty window is examined exactly once. The recorded window is the maximum total, and among those the earliest start and then the earliest end, because a candidate replaces the record only when it is strictly better under that order. If every total is negative, the record stays at 0, which is the empty trade. The algorithm therefore returns an optimal window.

### Complexity

| Case | Time | Extra space |
| --- | --- | --- |
| Best | Θ(n²) | Θ(n) |
| Average | Θ(n²) | Θ(n) |
| Worst | Θ(n²) | Θ(n) |

Every pair is examined, so the three cases match. Building the prefix is Θ(n) and does not change the quadratic bound. The prefix array is the extra memory.

## 2. Divide-and-conquer maximum subarray

### Pseudocode

```
function DIVIDE-AND-CONQUER(A, low, high):
    if low = high:
        return A[low] if A[low] > 0 else the empty trade
    mid ← ⌊(low + high) / 2⌋
    left ← DIVIDE-AND-CONQUER(A, low, mid)
    right ← DIVIDE-AND-CONQUER(A, mid+1, high)
    cross ← best sum that starts in [low, mid] and ends in [mid+1, high]
    return the better of left, right, and cross

function CROSSING(A, low, mid, high):
    scan from mid down to low, keeping the maximum suffix
    scan from mid+1 up to high, keeping the maximum prefix
    return suffix + prefix, unless that sum is ≤ 0
```

The suffix scan keeps the earliest start when two suffixes tie. The prefix scan keeps the earliest end when two prefixes tie.

### Correctness

A nonempty optimal window lies entirely in the left half, entirely in the right half, or it crosses `mid`. The first two cases are optimal for those halves by induction. A crossing window must include `A[mid]` and `A[mid+1]`, so it is a left suffix plus a right prefix. The maximum suffix and maximum prefix are found by the scans, and their sum is the best crossing window. The function returns the best of the three candidates, so it is optimal for `[low, high]`. The base case is a single element, or the empty trade when that element is not positive. The tie rule is applied in every candidate, so the earliest optimal window is the one returned.

### Complexity

Let T(n) be the time on n elements. The two recursive calls are on n/2 elements, and both scans together read n elements:

```
T(n) = 2 T(n/2) + Θ(n),    T(1) = Θ(1)
```

The Master Theorem gives T(n) = Θ(n log n). The same recurrence holds for every input, because the scans do not stop early.

| Case | Time | Extra space |
| --- | --- | --- |
| Best | Θ(n log n) | Θ(log n) stack |
| Average | Θ(n log n) | Θ(log n) stack |
| Worst | Θ(n log n) | Θ(log n) stack |

## 3. Kadane's scan

### Pseudocode

```
function KADANE(A[0..n-1]):
    best ← 0
    best window ← none
    current ← 0
    start ← 0
    for i ← 0 to n-1:
        if current < 0:
            current ← 0
            start ← i
        current ← current + A[i]
        if current > 0 and [start, i] is better than best:
            best ← current
            record [start, i]
    return best window
```

A non-positive running sum is discarded because extending it cannot help a later element. A zero sum is kept, so a tie still prefers the earlier start.

### Correctness

Consider the optimal window `[p, q]`, if one with positive sum exists. Kadane's running sum is reset only when it is negative. It is therefore not reset inside `[p, q]`: a negative running sum at some `r` in `(p, q]` would mean `[p, r]` is negative, and `[r+1, q]` would be a better window than `[p, q]`, contradicting optimality. So when the scan reaches `q`, `current` holds a sum at least as large as the optimal sum (it may have started earlier only by adding zeros). The recorded best is then at least the optimal sum. It cannot be larger, because it is the sum of some real window. The empty record covers the all-negative case. The same earliest-window rule used by the other two algorithms is applied on every update.

### Complexity

The loop body is constant work and runs once per element. No early exit is used.

| Case | Time | Extra space |
| --- | --- | --- |
| Best | Θ(n) | Θ(1) |
| Average | Θ(n) | Θ(1) |
| Worst | Θ(n) | Θ(1) |

Θ(n) is optimal in the comparison/addition model: any algorithm must read every element, since changing an unread element can change the answer.

## 4. Top-K by full sort

### Pseudocode

```
function TOP-K-SORT(items, k):
    if k ≤ 0: return []
    sort items by score descending, then by name ascending
    return the first min(k, length(items)) items
```

Python's sort is Timsort.

### Correctness

A total order is defined by `(−score, name)`. The first k positions of a sorted list are exactly the k best items under that order. If k is larger than the list, the whole sorted list is returned.

### Complexity

| Case | Time | Extra space |
| --- | --- | --- |
| Best | Θ(n) for Timsort on one long run | Θ(n) |
| Average | Θ(n log n) | Θ(n) |
| Worst | Θ(n log n) | Θ(n) |

Random market records do not form one long run, so the average bound is the one the benchmark should follow. The extra space is the temporary storage used by the sort.

## 5. Top-K by a size-K heap

### Pseudocode

```
function TOP-K-HEAP(items, k):
    if k ≤ 0: return []
    heap ← empty min-heap ordered by "worse than"
    for each item:
        if heap size < k:
            push item
        else if item is better than the heap minimum:
            replace the minimum with item
    return the heap contents in sorted order
```

"Worse" means a lower score, or the same score and a later name. The minimum of the heap is the weakest member of the current top K.

### Correctness

After the heap reaches size k, it holds k items, and every rejected item is worse than the current minimum. An item that belongs in the final top K can be rejected only if the heap already holds k items that are all better than it, which means it is not in the top K. Replacing the minimum when a better item arrives restores that invariant. At the end the heap is the top K, and the final sort only orders those k names.

### Complexity

Let the heap operations cost Θ(log k).

| Case | Time | Extra space |
| --- | --- | --- |
| Best | Θ(n + k log k), when the first k items are the answer and nothing later enters | Θ(k) |
| Average | Θ(n log k) as a safe bound; for random scores and fixed k the expected number of replacements is much smaller | Θ(k) |
| Worst | Θ(n log k), when every new item enters the heap | Θ(k) |

The final sort of k items is Θ(k log k) and is absorbed by those bounds when k ≤ n. This is the case the benchmark separates: best-case input puts the true top K first, worst-case input feeds strictly improving scores.

## What is not claimed

Quickselect is also implemented and checked in the tests. The required comparison is sort versus heap, so the benchmark tables use those two.

Brute force is timed through 10,000 records. At 100,000 and 1,000,000 records a single trial is hours in this Python implementation. The operation count at those sizes is still exact, `n(n+1)/2`, and the missing runtimes are the n² projection from the largest timed size. Those projected points are drawn dashed and are never described as measurements.
