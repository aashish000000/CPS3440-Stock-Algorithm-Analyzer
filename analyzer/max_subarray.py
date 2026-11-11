"""Maximum-subarray algorithms for one buy/sell window.

Daily price changes are integers. The sum of a contiguous block equals the
profit of buying at the start of that block and selling at the end. When every
block loses money, the best choice is to skip the trade (profit 0).

The three routines return the same window: the greatest profit, then the
earliest buy, then the earliest sell.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Subarray:
    """Inclusive bounds into the change array. Empty means do not trade."""

    total: int
    start: int | None = None
    end: int | None = None

    @property
    def empty(self) -> bool:
        return self.start is None


EMPTY = Subarray(0)


def _prefer(left: Subarray, right: Subarray) -> Subarray:
    if left.total != right.total:
        return left if left.total > right.total else right
    if left.total <= 0:
        return EMPTY
    if left.start != right.start:
        return left if left.start < right.start else right
    if left.end != right.end:
        return left if left.end < right.end else right
    return left


def brute_force(values: list[int]) -> Subarray:
    """Check every pair of endpoints. Time O(n^2), extra space O(n)."""

    best = EMPTY
    prefix = [0]
    for value in values:
        prefix.append(prefix[-1] + value)
    for start in range(len(values)):
        for end in range(start, len(values)):
            total = prefix[end + 1] - prefix[start]
            if total > 0:
                best = _prefer(best, Subarray(total, start, end))
    return best


def _crossing(values: list[int], low: int, mid: int, high: int) -> Subarray:
    """Best subarray that starts in the left half and ends in the right half."""

    best_left = None
    left_start = mid
    running = 0
    for index in range(mid, low - 1, -1):
        running += values[index]
        if best_left is None or running > best_left or (running == best_left and index < left_start):
            best_left = running
            left_start = index

    best_right = None
    right_end = mid + 1
    running = 0
    for index in range(mid + 1, high + 1):
        running += values[index]
        if best_right is None or running > best_right or (running == best_right and index < right_end):
            best_right = running
            right_end = index

    total = best_left + best_right
    if total <= 0:
        return EMPTY
    return Subarray(total, left_start, right_end)


def _divide(values: list[int], low: int, high: int) -> Subarray:
    if low == high:
        if values[low] > 0:
            return Subarray(values[low], low, high)
        return EMPTY
    mid = (low + high) // 2
    left = _divide(values, low, mid)
    right = _divide(values, mid + 1, high)
    cross = _crossing(values, low, mid, high)
    return _prefer(left, _prefer(right, cross))


def divide_and_conquer(values: list[int]) -> Subarray:
    """CLRS divide-and-conquer maximum subarray. Time O(n log n)."""

    if not values:
        return EMPTY
    return _divide(values, 0, len(values) - 1)


def kadane(values: list[int]) -> Subarray:
    """Single left-to-right scan. Time O(n), extra space O(1)."""

    best = EMPTY
    current = 0
    start = 0
    for index, value in enumerate(values):
        if current < 0:
            current = 0
            start = index
        current += value
        if current > 0:
            best = _prefer(best, Subarray(current, start, index))
    return best


ALGORITHMS: dict[str, Callable] = {
    "brute_force": brute_force,
    "divide_and_conquer": divide_and_conquer,
    "kadane": kadane,
}

COMPLEXITY = {
    "brute_force": "O(n^2)",
    "divide_and_conquer": "O(n log n)",
    "kadane": "O(n)",
}
