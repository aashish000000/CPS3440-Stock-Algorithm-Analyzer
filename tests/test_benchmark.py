import random
import unittest

from analyzer.benchmark import (
    brute_iterations,
    divide_and_conquer_iterations,
    heap_comparisons,
    kadane_iterations,
    sort_comparisons,
)
from analyzer.max_subarray import brute_force, divide_and_conquer, kadane
from analyzer.top_k import Scored, top_k_heap, top_k_sort


class BenchmarkMetricTests(unittest.TestCase):
    def test_iteration_counts_match_the_closed_forms(self) -> None:
        self.assertEqual(brute_iterations(1), 1)
        self.assertEqual(brute_iterations(4), 10)
        self.assertEqual(kadane_iterations(1000), 1000)
        self.assertGreater(divide_and_conquer_iterations(1000), 1000)
        self.assertLess(divide_and_conquer_iterations(1000), 1000 * 20)

    def test_divide_and_conquer_count_depends_only_on_length(self) -> None:
        self.assertEqual(divide_and_conquer_iterations(64), divide_and_conquer_iterations(64))
        smaller = divide_and_conquer_iterations(32)
        larger = divide_and_conquer_iterations(64)
        self.assertGreater(larger / 64, smaller / 32)

    def test_small_windows_still_agree_when_the_metrics_are_computed(self) -> None:
        values = [random.Random(4).randint(-5, 5) for _ in range(40)]
        self.assertEqual(brute_force(values), kadane(values))
        self.assertEqual(divide_and_conquer(values), kadane(values))
        self.assertEqual(brute_iterations(len(values)), 40 * 41 // 2)

    def test_top_k_counters_match_the_ranking(self) -> None:
        items = [Scored(f"T{index:02d}", index % 7) for index in range(30)]
        self.assertEqual(top_k_heap(items, 5), top_k_sort(items, 5))
        self.assertGreater(sort_comparisons(items, 5), 0)
        self.assertGreater(heap_comparisons(items, 5), 0)
        self.assertLess(heap_comparisons(items, 5), sort_comparisons(items, 5) * 2)


if __name__ == "__main__":
    unittest.main()
