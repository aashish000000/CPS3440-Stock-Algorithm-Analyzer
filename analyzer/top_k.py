"""Top-K selection algorithms.

Items are ordered by score descending, then by ticker ascending, so ties are
stable across every algorithm. The sort is merge sort and the heap is a
hand-written min-heap.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scored:
    ticker: str
    score: int


def _sort_key(item: Scored) -> tuple[int, str]:
    return (-item.score, item.ticker)


def _is_better(left: Scored, right: Scored) -> bool:
    """True when left belongs ahead of right in the Top-K order."""

    return _sort_key(left) < _sort_key(right)


def _is_worse(left: Scored, right: Scored) -> bool:
    """True when left is the weaker Top-K survivor and should sit nearer the heap root."""

    if left.score != right.score:
        return left.score < right.score
    return left.ticker > right.ticker


def _merge(left: list[Scored], right: list[Scored]) -> list[Scored]:
    merged: list[Scored] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if _is_better(right[j], left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    if i < len(left):
        merged.extend(left[i:])
    if j < len(right):
        merged.extend(right[j:])
    return merged


def merge_sort(items: list[Scored]) -> list[Scored]:
    """Stable merge sort. Best, average, and worst time are O(n log n)."""

    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    return _merge(merge_sort(items[:mid]), merge_sort(items[mid:]))


def top_k_sort(items: list[Scored], k: int) -> list[Scored]:
    """Merge-sort the whole list and keep the first k. Time O(n log n)."""

    if k <= 0:
        return []
    return merge_sort(items)[:k]


class MinHeap:
    """Min-heap of scored items. The root is the worst of the current top K.

    push, replace_root, and sift_down are the operations the Top-K scan uses.
    The heap is built from an empty array.
    """

    def __init__(self) -> None:
        self._data: list[Scored] = []

    def __len__(self) -> int:
        return len(self._data)

    def root(self) -> Scored:
        return self._data[0]

    def push(self, item: Scored) -> None:
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def replace_root(self, item: Scored) -> None:
        self._data[0] = item
        self.sift_down(0)

    def sift_down(self, index: int) -> None:
        size = len(self._data)
        while True:
            left = 2 * index + 1
            right = left + 1
            smallest = index
            if left < size and _is_worse(self._data[left], self._data[smallest]):
                smallest = left
            if right < size and _is_worse(self._data[right], self._data[smallest]):
                smallest = right
            if smallest == index:
                return
            self._data[index], self._data[smallest] = self._data[smallest], self._data[index]
            index = smallest

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if not _is_worse(self._data[index], self._data[parent]):
                return
            self._data[index], self._data[parent] = self._data[parent], self._data[index]
            index = parent

    def items(self) -> list[Scored]:
        return list(self._data)


def top_k_heap(items: list[Scored], k: int) -> list[Scored]:
    """Keep a size-k min-heap of the best items. Time O(n log k)."""

    if k <= 0:
        return []
    heap = MinHeap()
    for item in items:
        if len(heap) < k:
            heap.push(item)
        elif _is_worse(heap.root(), item):
            heap.replace_root(item)
    return merge_sort(heap.items())


def _median_index(items: list[Scored], low: int, high: int) -> int:
    """Median of three indexes, ordered by the Top-K key. No library sort."""

    mid = (low + high) // 2
    order = [low, mid, high]
    for position in range(1, 3):
        current = order[position]
        earlier = position - 1
        while earlier >= 0 and _is_better(items[current], items[order[earlier]]):
            order[earlier + 1] = order[earlier]
            earlier -= 1
        order[earlier + 1] = current
    return order[1]


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
    """Place the kth item with quickselect, then merge-sort those k. Average O(n)."""

    if k <= 0:
        return []
    chosen = list(items)
    if k >= len(chosen):
        return merge_sort(chosen)
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
    return merge_sort(chosen[:k])


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
