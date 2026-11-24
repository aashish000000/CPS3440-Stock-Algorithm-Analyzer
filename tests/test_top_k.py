import heapq
import random
import unittest

from analyzer.top_k import (
    ALGORITHMS,
    BinaryHeap,
    Scored,
    _sort_key,
    merge_sort,
    top_k_heap,
    top_k_quickselect,
    top_k_sort,
)


class TopKTests(unittest.TestCase):
    def test_ties_break_on_ticker(self) -> None:
        items = [Scored("ZZ", 5), Scored("AA", 5), Scored("MM", 5), Scored("BB", 9)]
        expected = [Scored("BB", 9), Scored("AA", 5), Scored("MM", 5)]
        for function in ALGORITHMS.values():
            self.assertEqual(function(items, 3), expected)

    def test_edges(self) -> None:
        items = [Scored("A", 1), Scored("B", 2)]
        for function in ALGORITHMS.values():
            self.assertEqual(function(items, 0), [])
            self.assertEqual(function(items, 5), [Scored("B", 2), Scored("A", 1)])

    def test_algorithms_agree(self) -> None:
        rng = random.Random(3440)
        for _ in range(40):
            items = [Scored(f"T{index:03d}", rng.randint(-20, 20)) for index in range(30)]
            k = rng.randint(0, 35)
            expected = top_k_sort(items, k)
            self.assertEqual(top_k_heap(items, k), expected)
            self.assertEqual(top_k_quickselect(items, k), expected)

    def test_merge_sort_matches_library_sorted(self) -> None:
        rng = random.Random(7)
        for size in (0, 1, 2, 3, 10, 57, 200):
            items = [Scored(f"T{index:03d}", rng.randint(-9, 9)) for index in range(size)]
            self.assertEqual(merge_sort(items), sorted(items, key=_sort_key))

    def test_merge_sort_does_not_change_its_input(self) -> None:
        items = [Scored("B", 1), Scored("A", 2)]
        merge_sort(items)
        self.assertEqual(items, [Scored("B", 1), Scored("A", 2)])

    def test_binary_heap_pops_in_library_heap_order(self) -> None:
        rng = random.Random(11)
        values = [rng.randint(-50, 50) for _ in range(100)]
        heap = BinaryHeap(lambda a, b: a.score < b.score)
        for value in values:
            heap.push(Scored("X", value))
        self.assertEqual(heap.peek().score, min(values))
        expected = heapq.nsmallest(3, values)
        taken = []
        for _ in range(3):
            taken.append(heap.peek().score)
            heap.replace_root(Scored("X", 10**9))
        self.assertEqual(taken, expected)


if __name__ == "__main__":
    unittest.main()
