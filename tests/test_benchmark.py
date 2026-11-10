import random
import unittest

from analyzer.benchmark import (
    _quadratic_prediction,
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

    def test_quadratic_projection_stays_in_milliseconds(self) -> None:
        # 200 ms at n = 10,000. One hundred times as many pairs is 20,000 ms,
        # not 20,000 seconds. The 1,000,000-record cell is 10,000 times the anchor.
        predicted = _quadratic_prediction({1_000: 2.0, 10_000: 200.0})
        self.assertEqual(predicted["anchor_n"], 10_000)
        self.assertAlmostEqual(predicted["predicted_ms"]["100000"], 20_000.0)
        self.assertAlmostEqual(predicted["predicted_ms"]["1000000"], 2_000_000.0)
        self.assertAlmostEqual(predicted["ms_per_n_squared"], 200.0 / 10_000**2)
        self.assertAlmostEqual(predicted["seconds_per_n_squared"], 200.0 / 10_000**2 / 1000.0)


if __name__ == "__main__":
    unittest.main()
