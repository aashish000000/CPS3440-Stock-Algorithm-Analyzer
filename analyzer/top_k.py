"""Top-K selection algorithms.

Items are ordered by score descending, then by ticker ascending, so ties are
stable across every algorithm.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass


@dataclass(frozen=True)
class Scored:
    ticker: str
    score: int


def _sort_key(item: Scored) -> tuple[int, str]:
    return (-item.score, item.ticker)


def _is_better(left: Scored, right: Scored) -> bool:
    return _sort_key(left) < _sort_key(right)


def top_k_sort(items: list[Scored], k: int) -> list[Scored]:
    """Sort the whole list and keep the first k. Time O(n log n)."""

    if k <= 0:
        return []
    return sorted(items, key=_sort_key)[:k]


class _WorseFirst:
    """Min-heap entry. The worst of the current top K is the smallest."""

    __slots__ = ("item",)

    def __init__(self, item: Scored) -> None:
        self.item = item

    def __lt__(self, other: _WorseFirst) -> bool:
        if self.item.score != other.item.score:
            return self.item.score < other.item.score
        return self.item.ticker > other.item.ticker


def top_k_heap(items: list[Scored], k: int) -> list[Scored]:
    """Keep a size-k min-heap of the best items. Time O(n log k)."""

    if k <= 0:
        return []
    heap: list[_WorseFirst] = []
    for item in items:
        node = _WorseFirst(item)
        if len(heap) < k:
            heapq.heappush(heap, node)
        elif heap[0] < node:
            heapq.heapreplace(heap, node)
    return sorted((node.item for node in heap), key=_sort_key)


def _median_index(items: list[Scored], low: int, high: int) -> int:
    mid = (low + high) // 2
    return sorted((low, mid, high), key=lambda index: _sort_key(items[index]))[1]


def _partition(items: list[Scored], low: int, high: int) -> int:
    pivot_at = _median_index(items, low, high)
    items[pivot_at], items[high] = items[high], items[pivot_at]
    pivot = items[high]
    store = low
    for index in range(low, high):
        if _is_better(items[index], pivot):
            items[store], items[index] = items[index], items[store]
            store += 1
    items[store], items[high] = items[high], items[store]
    return store


def top_k_quickselect(items: list[Scored], k: int) -> list[Scored]:
    """Place the kth item with quickselect, then sort those k. Average O(n)."""

    if k <= 0:
        return []
    chosen = list(items)
    if k >= len(chosen):
        return sorted(chosen, key=_sort_key)
    low = 0
    high = len(chosen) - 1
    target = k - 1
    while low < high:
        pivot = _partition(chosen, low, high)
        if pivot == target:
            break
        if pivot > target:
            high = pivot - 1
        else:
            low = pivot + 1
    return sorted(chosen[:k], key=_sort_key)


ALGORITHMS = {
    "full_sort": top_k_sort,
    "binary_heap": top_k_heap,
    "quickselect": top_k_quickselect,
}

COMPLEXITY = {
    "full_sort": "O(n log n)",
    "binary_heap": "O(n log k)",
    "quickselect": "O(n) average",
}
