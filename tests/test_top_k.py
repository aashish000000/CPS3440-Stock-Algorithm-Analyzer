import random
import unittest
from pathlib import Path

from analyzer.top_k import ALGORITHMS, Scored, merge_sort, top_k_heap, top_k_quickselect, top_k_sort


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

    def test_long_random_inputs_match_python_sorted(self) -> None:
        rng = random.Random(3440)
        lengths = (0, 1, 50, 200, 2_000)
        for length in lengths:
            scores = [0] * length
            if length:
                scores = [rng.randint(-(10**9), 10**9) for _ in range(length)]
                scores[0] = 0
                scores[-1] = 10**12
            items = [Scored(f"T{index:04d}", score) for index, score in enumerate(scores)]
            k = 0 if length == 0 else rng.randint(1, length + 5)
            expected = sorted(items, key=lambda item: (-item.score, item.ticker))[:k]
            self.assertEqual(merge_sort(items), sorted(items, key=lambda item: (-item.score, item.ticker)))
            self.assertEqual(top_k_sort(items, k), expected)
            self.assertEqual(top_k_heap(items, k), expected)
            self.assertEqual(top_k_quickselect(items, k), expected)

    def test_source_does_not_call_library_sort_or_heap(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "analyzer" / "top_k.py").read_text(encoding="utf-8")
        self.assertNotIn("heapq", source)
        self.assertNotIn("sorted(", source)
        self.assertNotIn(".sort(", source)


if __name__ == "__main__":
    unittest.main()
