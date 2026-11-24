"""Top-K selection algorithms.

Items are ordered by score descending, then by ticker ascending, so ties are
stable across every algorithm.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Scored:
    ticker: str
    score: int


Less = Callable[[Scored, Scored], bool]


def _sort_key(item: Scored) -> tuple[int, str]:
    return (-item.score, item.ticker)


def _is_better(left: Scored, right: Scored) -> bool:
    return _sort_key(left) < _sort_key(right)


def _is_worse(left: Scored, right: Scored) -> bool:
    return _is_better(right, left)


def merge_sort(items: list[Scored], less: Less = _is_better) -> list[Scored]:
    """Stable top-down merge sort written for this project. Time O(n log n).

    ``less(a, b)`` is True when ``a`` must come before ``b``. The caller's list
    is not modified. A counting wrapper around ``less`` measures comparisons.
    """

    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], less)
    right = merge_sort(items[middle:], less)
    merged: list[Scored] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if less(right[j], left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


class BinaryHeap:
    """Array-backed binary heap written for this project.

    The root is the item that ``less`` ranks first. Parent of index i is
    (i - 1) // 2 and its children are 2i + 1 and 2i + 2.
    """

    def __init__(self, less: Less) -> None:
        self._less = less
        self._items: list[Scored] = []

    def __len__(self) -> int:
        return len(self._items)

    def peek(self) -> Scored:
        return self._items[0]

    def push(self, item: Scored) -> None:
        """Append and sift up. Time O(log n)."""

        items = self._items
        items.append(item)
        child = len(items) - 1
        while child > 0:
            parent = (child - 1) // 2
            if not self._less(items[child], items[parent]):
                break
            items[child], items[parent] = items[parent], items[child]
            child = parent

    def replace_root(self, item: Scored) -> None:
        """Overwrite the root and sift down. Time O(log n)."""

        items = self._items
        items[0] = item
        parent = 0
        size = len(items)
        while True:
            left = 2 * parent + 1
            right = left + 1
            first = parent
            if left < size and self._less(items[left], items[first]):
                first = left
            if right < size and self._less(items[right], items[first]):
                first = right
            if first == parent:
                break
            items[parent], items[first] = items[first], items[parent]
            parent = first

    def to_list(self) -> list[Scored]:
        return list(self._items)


def top_k_sort(items: list[Scored], k: int, less: Less = _is_better) -> list[Scored]:
    """Merge-sort the whole list and keep the first k. Time O(n log n)."""

    if k <= 0:
        return []
    return merge_sort(items, less)[:k]


def top_k_heap(items: list[Scored], k: int, less: Less = _is_better) -> list[Scored]:
    """Keep a size-k heap whose root is the worst of the best k. O(n log k)."""

    if k <= 0:
        return []
    heap = BinaryHeap(lambda a, b: less(b, a))
    for item in items:
        if len(heap) < k:
            heap.push(item)
        elif less(item, heap.peek()):
            heap.replace_root(item)
    return merge_sort(heap.to_list(), less)


def _median_index(items: list[Scored], low: int, high: int) -> int:
    mid = (low + high) // 2
    a, b, c = low, mid, high
    if _is_better(items[b], items[a]):
        a, b = b, a
    if _is_better(items[c], items[b]):
        b = c
        if _is_better(items[b], items[a]):
            b = a
    return b


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
